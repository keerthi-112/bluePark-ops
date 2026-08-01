from django.contrib.auth.models import User

from core.constants import ROLE_ADMIN, ROLE_CHEF, ROLE_MANAGER, ROLE_WAITER

from .models import Notification


def notify(recipient, message, target=None):
    return Notification.objects.create(
        recipient=recipient,
        message=message,
        target_content_type=None if target is None else _content_type(target),
        target_object_id=None if target is None else target.pk,
    )


def _content_type(target):
    from django.contrib.contenttypes.models import ContentType
    return ContentType.objects.get_for_model(target)


def notify_role(roles, message, target=None):
    users = User.objects.filter(profile__role__in=roles)
    return [notify(user, message, target=target) for user in users]


def notify_kitchen_staff(message, target=None):
    return notify_role([ROLE_WAITER, ROLE_CHEF, ROLE_MANAGER, ROLE_ADMIN], message, target=target)


def notify_managers(message, target=None):
    return notify_role([ROLE_MANAGER, ROLE_ADMIN], message, target=target)


def has_unread_notification_for(recipient, target):
    return Notification.objects.filter(
        recipient=recipient,
        target_content_type=_content_type(target),
        target_object_id=target.pk,
        is_read=False,
    ).exists()
