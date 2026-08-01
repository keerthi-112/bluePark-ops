"""Orchestrates the copilot's answer: build context, construct the
prompt, call the configured provider. This is the ONLY thing views/API
code should ever call -- never ai_copilot.providers directly -- so the
provider and prompt format can change without touching the view layer."""

import json
import logging

from .context import build_operations_context
from .providers import get_provider

logger = logging.getLogger('ai_copilot')

PROMPT_TEMPLATE = """You are BluePark's AI Operations Copilot, helping a restaurant manager \
understand their business. Answer the manager's question using ONLY the data \
below -- do not invent numbers. Be concise and specific, and cite the actual \
figures from the data. If the data doesn't contain what's needed to answer, say \
so plainly instead of guessing.

Data for {start} to {end}:
{context_json}

Manager's question: {question}
"""


def build_prompt(question, context):
    return PROMPT_TEMPLATE.format(
        start=context['date_range']['start'],
        end=context['date_range']['end'],
        context_json=json.dumps(context, indent=2, default=str),
        question=question,
    )


def answer_question(question, start, end):
    """Returns the copilot's answer as a string. Raises
    ai_copilot.providers.AIProviderError on failure -- callers (the API
    view) decide how to surface that as an HTTP response."""

    context = build_operations_context(start, end)
    prompt = build_prompt(question, context)
    logger.info('AI copilot question: %r (range %s to %s)', question, context['date_range']['start'], context['date_range']['end'])
    return get_provider().generate(prompt)
