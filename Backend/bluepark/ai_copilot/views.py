from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from core.constants import ROLE_ADMIN, ROLE_MANAGER

MANAGER_ROLES = {ROLE_MANAGER, ROLE_ADMIN}


@login_required
def chat(request):
    role = getattr(getattr(request.user, 'profile', None), 'role', None)
    if role not in MANAGER_ROLES:
        raise PermissionDenied('The AI copilot is only available to Manager/Admin.')

    return render(request, 'ai_copilot_chat.html')
