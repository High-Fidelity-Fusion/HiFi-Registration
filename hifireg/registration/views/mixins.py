from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist

from registration.models import Registration, Order


# Set self.registration; redirect if registration does not exist.
class RegistrationRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        try:
            self.registration = Registration.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return redirect('registration')
        return super().dispatch(request, *args, **kwargs)


# Set self.order; redirect if order does not exist.
class OrderRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        try:
            self.order = Order.objects.get(session = Session.objects.get(pk=request.session.session_key))
        except ObjectDoesNotExist:
            return redirect('order')
        return super().dispatch(request, *args, **kwargs)
