from django.conf import settings
from django.db import models

from core.constants import ROLE_CHOICES, ROLE_CUSTOMER


class Profile(models.Model):
    """Extends Django's built-in User with the role BluePark actually
    operates on (customer/waiter/chef/manager/admin), without touching
    the User model itself."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_CUSTOMER)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f'{self.user.username} ({self.get_role_display()})'
