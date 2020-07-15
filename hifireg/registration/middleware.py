from datetime import datetime

from django.conf import settings
from django.shortcuts import redirect
from django.urls import resolve


class RefreshSessions:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.session['last_touch'] = datetime.now().timestamp()

        response = self.get_response(request)
        return response


class CheckBetaPassword:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_url = resolve(request.path_info).url_name
        if not current_url == 'beta_login':
            if not request.session.get('site_password') and settings.BETA_PASSWORD:
                return redirect('beta_login')

        response = self.get_response(request)
        return response