from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from ai_copilot import services
from ai_copilot.providers import AIProviderError, GeminiProvider


class GeminiProviderTests(TestCase):
    def test_missing_api_key_raises_clear_error(self):
        with self.assertRaises(AIProviderError) as ctx:
            GeminiProvider(api_key='')
        self.assertIn('GEMINI_API_KEY', str(ctx.exception))

    def test_generate_returns_model_text(self):
        provider = GeminiProvider(api_key='fake-key-for-test')
        fake_response = MagicMock(text='Mocked answer.')
        with patch('google.genai.Client') as MockClient:
            MockClient.return_value.models.generate_content.return_value = fake_response
            result = provider.generate('a prompt')
        self.assertEqual(result, 'Mocked answer.')

    def test_network_failure_wrapped_as_provider_error(self):
        provider = GeminiProvider(api_key='fake-key-for-test')
        with patch('google.genai.Client') as MockClient:
            MockClient.return_value.models.generate_content.side_effect = ConnectionError('down')
            with self.assertRaises(AIProviderError):
                provider.generate('a prompt')

    def test_empty_response_raises_provider_error(self):
        provider = GeminiProvider(api_key='fake-key-for-test')
        fake_response = MagicMock(text='')
        with patch('google.genai.Client') as MockClient:
            MockClient.return_value.models.generate_content.return_value = fake_response
            with self.assertRaises(AIProviderError):
                provider.generate('a prompt')


class AnswerQuestionTests(TestCase):
    def test_builds_context_and_delegates_to_provider(self):
        fake_provider = MagicMock()
        fake_provider.generate.return_value = 'The answer.'
        now = timezone.now()

        with patch('ai_copilot.services.get_provider', return_value=fake_provider):
            answer = services.answer_question('How is revenue?', now - timezone.timedelta(days=7), now)

        self.assertEqual(answer, 'The answer.')
        prompt_sent = fake_provider.generate.call_args[0][0]
        self.assertIn('How is revenue?', prompt_sent)
        self.assertIn('"revenue"', prompt_sent)
        self.assertIn('"customer_feedback"', prompt_sent)


class AskCopilotAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = User.objects.create_user('api_customer', password='x')
        self.manager = User.objects.create_user('api_manager', password='x')
        self.manager.profile.role = 'manager'
        self.manager.profile.save()
        self.url = reverse('api_ai_ask')

    def test_anonymous_forbidden(self):
        response = self.client.post(self.url, {'question': 'test'}, format='json')
        self.assertEqual(response.status_code, 403)

    def test_customer_forbidden(self):
        self.client.force_authenticate(self.customer)
        response = self.client.post(self.url, {'question': 'test'}, format='json')
        self.assertEqual(response.status_code, 403)

    def test_manager_missing_question(self):
        self.client.force_authenticate(self.manager)
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_manager_success(self):
        self.client.force_authenticate(self.manager)
        fake_provider = MagicMock()
        fake_provider.generate.return_value = 'Revenue is up 10% this week.'
        with patch('ai_copilot.services.get_provider', return_value=fake_provider):
            response = self.client.post(self.url + '?range=7d', {'question': 'How is revenue?'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['answer'], 'Revenue is up 10% this week.')
        self.assertEqual(response.data['range'], '7d')

    def test_provider_failure_returns_503_not_500(self):
        self.client.force_authenticate(self.manager)
        with patch('ai_copilot.services.get_provider', side_effect=AIProviderError('No key configured.')):
            response = self.client.post(self.url, {'question': 'How is revenue?'}, format='json')
        self.assertEqual(response.status_code, 503)
        self.assertIn('No key configured.', response.data['error'])
