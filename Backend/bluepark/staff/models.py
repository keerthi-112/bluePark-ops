from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


class Employee(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employee')
    position = models.CharField(max_length=100, blank=True)
    hire_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} ({self.position or self.user.profile.get_role_display()})'


class Shift(TimeStampedModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='shifts')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f'{self.employee.user.username}: {self.start_time:%Y-%m-%d %H:%M} - {self.end_time:%H:%M}'


class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance')
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='attendance', null=True, blank=True)
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-check_in']
        verbose_name_plural = 'attendance records'

    def __str__(self):
        return f'{self.employee.user.username}: {self.check_in}'
