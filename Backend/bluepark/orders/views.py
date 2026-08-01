from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import Order
from .services import EmptyCartError, create_order_from_cart, get_active_cart


@login_required
def checkout(request):
    cart = get_active_cart(request.user)
    if request.method == 'POST':
        address_parts = [
            request.POST.get('address', ''),
            request.POST.get('city', ''),
            request.POST.get('state', ''),
            request.POST.get('zip', ''),
        ]
        delivery_address = ', '.join(part for part in address_parts if part)
        phone = request.POST.get('phone', '')

        try:
            create_order_from_cart(
                cart,
                customer=request.user,
                order_type=Order.ORDER_TYPE_DELIVERY,
                payment_method=Order.PAYMENT_METHOD_COD,
                delivery_address=delivery_address,
                phone=phone,
            )
        except EmptyCartError:
            messages.info(request, 'Your cart is empty -- add something from the menu first.')
            return redirect('home')
        return redirect('waiting')

    return render(request, 'checkout.html', {'cart': cart})


def waiting(request):
    return render(request, 'waiting.html')
