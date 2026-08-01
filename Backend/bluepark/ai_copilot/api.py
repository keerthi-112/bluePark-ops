from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from analytics.dateranges import resolve_range
from core.permissions import IsManagerOrAdmin

from .providers import AIProviderError
from .services import answer_question


class AskCopilotView(APIView):
    """POST {"question": "..."} -- date range comes from the query
    string (?range=7d or ?range=custom&start=&end=), same convention
    the rest of the API uses, so this reuses
    analytics.dateranges.resolve_range unchanged rather than
    reimplementing range parsing for a POST body."""

    permission_classes = [IsManagerOrAdmin]

    def post(self, request):
        question = (request.data.get('question') or '').strip()
        if not question:
            return Response({'error': 'A question is required.'}, status=status.HTTP_400_BAD_REQUEST)

        start, end, range_key = resolve_range(request)

        try:
            answer = answer_question(question, start, end)
        except AIProviderError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response({
            'answer': answer,
            'range': range_key,
            'start': start.date().isoformat(),
            'end': end.date().isoformat(),
        })
