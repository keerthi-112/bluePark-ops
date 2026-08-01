"""Provider abstraction for the AI Operations Copilot. Views and
services never import a specific AI vendor's SDK directly -- they call
get_provider().generate(prompt), and get_provider() reads
settings.AI_PROVIDER to decide which class to instantiate. Adding a
second provider later (OpenAI, Claude, ...) means adding one class
and one branch here, not touching anything that calls it."""

import logging
from abc import ABC, abstractmethod

from django.conf import settings

logger = logging.getLogger('ai_copilot')


class AIProviderError(Exception):
    """Raised for any provider failure (bad key, network, quota, ...)
    -- callers catch this one type regardless of which vendor is
    configured underneath."""


class AIProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Returns the model's text response, or raises AIProviderError."""


class GeminiProvider(AIProvider):
    """Wraps google-genai. The import is local to __init__ rather than
    module-level so importing ai_copilot.providers doesn't require the
    package to be installed unless Gemini is actually selected."""

    DEFAULT_MODEL = 'gemini-2.0-flash'

    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or getattr(settings, 'GEMINI_MODEL', self.DEFAULT_MODEL)
        if not self.api_key:
            raise AIProviderError(
                'GEMINI_API_KEY is not configured. Set it in your .env file -- '
                'see .env.example and the README\'s AI setup section.'
            )

    def generate(self, prompt: str) -> str:
        from google import genai
        from google.genai import errors as genai_errors

        try:
            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(model=self.model, contents=prompt)
        except genai_errors.APIError as exc:
            logger.error('Gemini API error: %s', exc)
            raise AIProviderError('The AI provider returned an error. Please try again shortly.') from exc
        except Exception as exc:  # network errors, etc. -- not raised as genai_errors.APIError
            logger.exception('Unexpected error calling Gemini')
            raise AIProviderError('Could not reach the AI provider. Please try again shortly.') from exc

        text = getattr(response, 'text', None)
        if not text:
            logger.error('Gemini returned an empty response: %r', response)
            raise AIProviderError('The AI provider returned an empty response.')
        return text


_PROVIDERS = {
    'gemini': GeminiProvider,
}


def get_provider() -> AIProvider:
    provider_key = getattr(settings, 'AI_PROVIDER', 'gemini')
    try:
        provider_class = _PROVIDERS[provider_key]
    except KeyError:
        raise AIProviderError(f"Unknown AI_PROVIDER '{provider_key}'. Valid options: {', '.join(_PROVIDERS)}")
    return provider_class()
