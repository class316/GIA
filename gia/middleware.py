from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils import timezone


class SessionInactivityTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            now = timezone.now().timestamp()
            last_activity = request.session.get('last_activity')
            timeout = getattr(settings, 'SESSION_COOKIE_AGE', 600)

            if last_activity and now - float(last_activity) > timeout:
                logout(request)
                messages.warning(request, 'Tu sesión expiró por inactividad')
                return redirect(settings.LOGIN_URL)

            request.session['last_activity'] = now

        return self.get_response(request)
