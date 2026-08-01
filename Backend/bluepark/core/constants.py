"""Single source of truth for staff roles, shared by accounts.Profile and
core.permissions so the two never drift out of sync with each other."""

ROLE_CUSTOMER = 'customer'
ROLE_WAITER = 'waiter'
ROLE_CHEF = 'chef'
ROLE_MANAGER = 'manager'
ROLE_ADMIN = 'admin'

ROLE_CHOICES = [
    (ROLE_CUSTOMER, 'Customer'),
    (ROLE_WAITER, 'Waiter'),
    (ROLE_CHEF, 'Chef'),
    (ROLE_MANAGER, 'Manager'),
    (ROLE_ADMIN, 'Admin'),
]

STAFF_ROLES = {ROLE_WAITER, ROLE_CHEF, ROLE_MANAGER, ROLE_ADMIN}
