from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.constants import STAFF_ROLES
from core.permissions import IsStaffRole

from . import services
from .models import Order
from .serializers import (
    AddCartItemSerializer,
    CartSerializer,
    CreateOrderSerializer,
    OrderSerializer,
    OrderStatusUpdateSerializer,
)


def _is_staff_role(user):
    profile = getattr(user, 'profile', None)
    return getattr(profile, 'role', None) in STAFF_ROLES


class CartView(APIView):
    """GET the caller's active cart (auto-created if they don't have one)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = services.get_active_cart(request.user)
        return Response(CartSerializer(cart).data)


class CartItemListView(APIView):
    """POST to add an item to the caller's active cart."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart = services.get_active_cart(request.user)
        services.add_item_to_cart(cart, **serializer.validated_data)
        cart.refresh_from_db()
        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)


class CartItemDetailView(APIView):
    """DELETE to remove a single item from the caller's active cart."""

    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        cart = services.get_active_cart(request.user)
        services.remove_item_from_cart(cart, item_id)
        cart.refresh_from_db()
        return Response(CartSerializer(cart).data)


class OrderListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if _is_staff_role(request.user):
            orders = Order.objects.select_related('customer').prefetch_related('items')
        else:
            orders = Order.objects.filter(customer=request.user).prefetch_related('items')
        return Response(OrderSerializer(orders, many=True).data)

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart = services.get_active_cart(request.user)
        try:
            order = services.create_order_from_cart(cart, customer=request.user, **serializer.validated_data)
        except services.EmptyCartError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        if order.customer_id != request.user.id and not _is_staff_role(request.user):
            raise PermissionDenied('You do not have access to this order.')
        return Response(OrderSerializer(order).data)


class OrderStatusUpdateView(APIView):
    """PATCH to advance an order's status. Chef/Waiter/Manager/Admin only."""

    permission_classes = [IsStaffRole]

    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        serializer = OrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.advance_order_status(order, serializer.validated_data['status'], changed_by=request.user)
        return Response(OrderSerializer(order).data)
