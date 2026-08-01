from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsManagerOrAdmin

from . import services
from .models import Ingredient, StockMovement
from .serializers import CreateStockMovementSerializer, IngredientSerializer, StockMovementSerializer


class IngredientListCreateView(ListCreateAPIView):
    """Read: Manager/Admin (kitchen staff see stock through the low-stock
    view/kitchen queue, not the raw ledger). Write: Manager/Admin."""

    queryset = Ingredient.objects.select_related('supplier').all()
    serializer_class = IngredientSerializer
    permission_classes = [IsManagerOrAdmin]


class StockMovementListCreateView(APIView):
    permission_classes = [IsManagerOrAdmin]

    def get(self, request):
        movements = StockMovement.objects.select_related('ingredient')
        return Response(StockMovementSerializer(movements, many=True).data)

    def post(self, request):
        serializer = CreateStockMovementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        movement = services.adjust_stock(created_by=request.user, **serializer.validated_data)
        return Response(StockMovementSerializer(movement).data, status=status.HTTP_201_CREATED)


class LowStockView(APIView):
    permission_classes = [IsManagerOrAdmin]

    def get(self, request):
        return Response(IngredientSerializer(services.get_low_stock_ingredients(), many=True).data)
