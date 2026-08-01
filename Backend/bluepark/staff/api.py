from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsManagerOrAdmin

from . import services
from .models import Attendance, Employee, Shift
from .serializers import AttendanceSerializer, EmployeeSerializer, ShiftSerializer


class EmployeeListCreateView(ListCreateAPIView):
    queryset = Employee.objects.select_related('user', 'user__profile').all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsManagerOrAdmin]


class ShiftListCreateView(ListCreateAPIView):
    queryset = Shift.objects.select_related('employee__user').all()
    serializer_class = ShiftSerializer
    permission_classes = [IsManagerOrAdmin]


class MyShiftsView(APIView):
    """Any authenticated staff member's own upcoming shifts."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        employee = getattr(request.user, 'employee', None)
        if employee is None:
            return Response([])
        return Response(ShiftSerializer(services.get_upcoming_shifts(employee), many=True).data)


class ClockInView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        employee = getattr(request.user, 'employee', None)
        if employee is None:
            return Response({'detail': 'No employee record for this account.'}, status=status.HTTP_400_BAD_REQUEST)
        shift_id = request.data.get('shift')
        shift = Shift.objects.filter(pk=shift_id, employee=employee).first() if shift_id else None
        attendance = services.clock_in(employee, shift=shift)
        return Response(AttendanceSerializer(attendance).data, status=status.HTTP_201_CREATED)


class ClockOutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        employee = getattr(request.user, 'employee', None)
        attendance = Attendance.objects.filter(pk=pk, employee=employee).first() if employee else None
        if attendance is None:
            return Response({'detail': 'Attendance record not found.'}, status=status.HTTP_404_NOT_FOUND)
        services.clock_out(attendance)
        return Response(AttendanceSerializer(attendance).data)
