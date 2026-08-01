"""Custom signals other apps can subscribe to without `orders` needing
to know they exist (inventory deducts stock, notifications alerts
kitchen staff, etc.) -- keeps this app open for extension without
modification.

Not django.db.models.signals.post_save on Order: create_order_from_cart
creates the Order row, then bulk_creates its OrderItems (bulk_create
does not fire per-instance signals), so a post_save receiver would fire
before any items exist. order_placed is sent explicitly once the whole
order (items included) is ready.
"""

import django.dispatch

order_placed = django.dispatch.Signal()  # providing_args: ['order']

order_status_changed = django.dispatch.Signal()  # providing_args: ['order', 'old_status', 'new_status', 'changed_by']
