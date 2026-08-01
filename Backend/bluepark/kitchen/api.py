from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsKitchenStaff
from orders.serializers import OrderSerializer
from orders.services import get_active_orders


class KitchenQueueView(APIView):
    """GET the active order queue, oldest first. Chef/Manager/Admin only."""

    permission_classes = [IsKitchenStaff]

    def get(self, request):
        return Response(OrderSerializer(get_active_orders(), many=True).data)
