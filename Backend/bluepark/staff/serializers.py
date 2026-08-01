from rest_framework import serializers

from .models import Attendance, Employee, Shift


class EmployeeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    role = serializers.CharField(source='user.profile.role', read_only=True)

    class Meta:
        model = Employee
        fields = ['id', 'user', 'username', 'role', 'position', 'hire_date']


class ShiftSerializer(serializers.ModelSerializer):
    employee_username = serializers.CharField(source='employee.user.username', read_only=True)

    class Meta:
        model = Shift
        fields = ['id', 'employee', 'employee_username', 'start_time', 'end_time']


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['id', 'employee', 'shift', 'check_in', 'check_out']
        read_only_fields = ['id', 'employee', 'check_in', 'check_out']
