from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect

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


# Use a CBV as an FBV: Overrides dispatch method of CBV with fbv() method.
# Implement the fbv() method as you would a normal FBV.
# This class should be added just before the CBV class in the inheritance sequence.
# You get the benefit of dispatch() mixins, class/instance variables, and inheritance, 
# with the simplicity of FBVs.
# Recommended: Use with the TemplateView and manually call super().get(request)
# instead of render(). This provides useful context for free and let's you set
# template as a class variable.
class FunctionBasedView:
    def dispatch(self, request, *args, **kwargs):
        return self.fbv(request)
        