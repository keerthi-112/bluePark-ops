from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView, get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsKitchenStaff, IsManagerOrAdmin

from .models import Category, Menu
from .serializers import AvailabilitySerializer, CategorySerializer, MenuItemSerializer


class CategoryListCreateView(ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsManagerOrAdmin()]
        return [AllowAny()]


class MenuItemListCreateView(ListCreateAPIView):
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsManagerOrAdmin()]
        return [AllowAny()]

    def get_queryset(self):
        qs = Menu.objects.select_related('category').all()
        category_slug = self.request.query_params.get('category')
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        is_available = self.request.query_params.get('is_available')
        if is_available is not None:
            qs = qs.filter(is_available=is_available.lower() in ('1', 'true', 'yes'))
        return qs


class MenuItemDetailView(RetrieveUpdateAPIView):
    queryset = Menu.objects.select_related('category').all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH'):
            return [IsManagerOrAdmin()]
        return [AllowAny()]


class MenuItemAvailabilityView(APIView):
    """A narrower endpoint than the general item update: lets Chef (not
    just Manager/Admin) 86 an item without granting them edit rights
    over price/description/category."""

    permission_classes = [IsKitchenStaff]

    def patch(self, request, pk):
        item = get_object_or_404(Menu, pk=pk)
        serializer = AvailabilitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item.is_available = serializer.validated_data['is_available']
        item.save(update_fields=['is_available'])
        return Response(MenuItemSerializer(item).data)
