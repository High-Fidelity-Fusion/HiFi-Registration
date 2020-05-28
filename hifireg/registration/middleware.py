from datetime import datetime


class RefreshSessions:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.session['last_touch'] = datetime.now().timestamp()

        response = self.get_response(request)
        return response
