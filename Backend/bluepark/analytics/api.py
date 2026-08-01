from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsManagerOrAdmin

from . import services
from .dateranges import resolve_range


class AnalyticsSummaryView(APIView):
    """One combined payload for the whole analytics dashboard -- the
    page fetches this once per filter change and redraws every chart,
    rather than one request per section."""

    permission_classes = [IsManagerOrAdmin]

    def get(self, request):
        start, end, range_key = resolve_range(request)

        return Response({
            'range': range_key,
            'start': start.date().isoformat(),
            'end': end.date().isoformat(),
            'revenue': services.get_revenue_summary(start, end),
            'orders': services.get_orders_summary(start, end),
        })
