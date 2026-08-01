from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase

from core.permissions import IsCustomer, IsKitchenStaff, IsManagerOrAdmin, IsStaffRole


class RolePermissionTests(TestCase):
    """Unit-level: exercise has_permission() directly rather than
    through a real view/URL, since that's all these classes do."""

    def setUp(self):
        self.factory = RequestFactory()
        self.customer = User.objects.create_user('perm_customer', password='x')
        self.waiter = User.objects.create_user('perm_waiter', password='x')
        self.waiter.profile.role = 'waiter'
        self.waiter.profile.save()
        self.manager = User.objects.create_user('perm_manager', password='x')
        self.manager.profile.role = 'manager'
        self.manager.profile.save()

    def _request_as(self, user):
        request = self.factory.get('/')
        request.user = user
        return request

    def test_anonymous_user_denied_everywhere(self):
        request = self._request_as(AnonymousUser())
        self.assertFalse(IsCustomer().has_permission(request, None))
        self.assertFalse(IsManagerOrAdmin().has_permission(request, None))

    def test_customer_role_gating(self):
        request = self._request_as(self.customer)
        self.assertTrue(IsCustomer().has_permission(request, None))
        self.assertFalse(IsManagerOrAdmin().has_permission(request, None))
        self.assertFalse(IsStaffRole().has_permission(request, None))

    def test_waiter_is_staff_but_not_kitchen_or_manager(self):
        request = self._request_as(self.waiter)
        self.assertTrue(IsStaffRole().has_permission(request, None))
        self.assertFalse(IsKitchenStaff().has_permission(request, None))
        self.assertFalse(IsManagerOrAdmin().has_permission(request, None))

    def test_manager_has_manager_and_staff_access(self):
        request = self._request_as(self.manager)
        self.assertTrue(IsManagerOrAdmin().has_permission(request, None))
        self.assertTrue(IsStaffRole().has_permission(request, None))
        self.assertTrue(IsKitchenStaff().has_permission(request, None))
        self.assertFalse(IsCustomer().has_permission(request, None))
