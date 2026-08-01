"""Notifies each employee scheduled to work today, once per shift.

No Celery/cron is wired up yet (Phase 3+), so run this manually or from
an OS-level scheduler (cron/Task Scheduler) once a day, e.g.:
    python manage.py notify_shift_reminders
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from notifications import services
from staff.models import Shift


class Command(BaseCommand):
    help = "Send a same-day reminder notification for every shift starting today."

    def handle(self, *args, **options):
        today = timezone.localdate()
        shifts = Shift.objects.filter(start_time__date=today).select_related('employee__user')

        sent = 0
        for shift in shifts:
            if services.has_unread_notification_for(shift.employee.user, shift):
                continue
            services.notify(
                shift.employee.user,
                f'Reminder: your shift today runs {shift.start_time:%H:%M}-{shift.end_time:%H:%M}.',
                target=shift,
            )
            sent += 1

        self.stdout.write(self.style.SUCCESS(f'Sent {sent} shift reminder(s) for {today}.'))
