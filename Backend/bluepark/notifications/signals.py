from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.constants import ROLE_ADMIN, ROLE_MANAGER
from inventory.models import StockMovement
from orders.signals import order_placed

from . import services


def handle_order_placed(sender, order, **kwargs):
    services.notify_kitchen_staff(f'New order #{order.id} from {order.customer.username}.', target=order)


order_placed.connect(handle_order_placed, dispatch_uid='notifications_new_order')


@receiver(post_save, sender=StockMovement, dispatch_uid='notifications_low_stock')
def handle_stock_movement(sender, instance, created, **kwargs):
    if not created:
        return
    ingredient = instance.ingredient
    if not ingredient.is_low_stock:
        return
    # Only notify once per unread alert -- otherwise every purchase/waste
    # entry on an ingredient that's still low would re-notify managers.
    for user in User.objects.filter(profile__role__in=[ROLE_MANAGER, ROLE_ADMIN]):
        if not services.has_unread_notification_for(user, ingredient):
            services.notify(user, f'{ingredient.name} is low on stock ({ingredient.current_stock}{ingredient.unit}).', target=ingredient)
