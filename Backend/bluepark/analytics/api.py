from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsManagerOrAdmin

from .dateranges import resolve_range
from .services import build_summary_payload


class AnalyticsSummaryView(APIView):
    """One combined payload for the whole analytics dashboard -- the
    page fetches this once per filter change and redraws every chart,
    rather than one request per section."""

    permission_classes = [IsManagerOrAdmin]

    def get(self, request):
        start, end, range_key = resolve_range(request)
        return Response(build_summary_payload(start, end, range_key))
