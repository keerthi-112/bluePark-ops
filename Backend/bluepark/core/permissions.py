"""Role-based DRF permission classes.

Every class checks `request.user.profile.role` rather than Django's
built-in `is_staff`/`is_superuser`, since BluePark's roles (customer,
waiter, chef, manager, admin) are a separate concept from Django's own
staff/superuser flags.
"""

from rest_framework.permissions import BasePermission

from .constants import ROLE_ADMIN, ROLE_CHEF, ROLE_CUSTOMER, ROLE_MANAGER, ROLE_WAITER, STAFF_ROLES


def _role(request):
    profile = getattr(request.user, 'profile', None)
    return getattr(profile, 'role', None)


class HasRole(BasePermission):
    """Base class: subclass and set `allowed_roles`."""

    allowed_roles = frozenset()

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and _role(request) in self.allowed_roles)


class IsCustomer(HasRole):
    allowed_roles = {ROLE_CUSTOMER}


class IsWaiter(HasRole):
    allowed_roles = {ROLE_WAITER}


class IsChef(HasRole):
    allowed_roles = {ROLE_CHEF}


class IsManager(HasRole):
    allowed_roles = {ROLE_MANAGER}


class IsAdminRole(HasRole):
    allowed_roles = {ROLE_ADMIN}


class IsStaffRole(HasRole):
    """Any operational role: waiter, chef, manager, or admin."""

    allowed_roles = STAFF_ROLES


class IsKitchenStaff(HasRole):
    """Chef, manager, or admin — roles allowed to run the kitchen queue."""

    allowed_roles = {ROLE_CHEF, ROLE_MANAGER, ROLE_ADMIN}


class IsManagerOrAdmin(HasRole):
    allowed_roles = {ROLE_MANAGER, ROLE_ADMIN}
