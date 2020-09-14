from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect

from registration.models import Registration, Order, Payment
from .stripe_helpers import get_stripe_checkout_session_total


# A magical decorator that provides syntactic cleanliness for chaining dispatch
# mixins. It replaces "this_class" with an empty class that inherits first from
# "base_class" and then from "this_class".
def chain_with(base_class):
    def chainer(this_class):
        return type(this_class.__name__, (base_class, this_class), {})
    return chainer


@chain_with(LoginRequiredMixin)
class RegistrationRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        try:
            self.registration = Registration.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return redirect('index')
        return super().dispatch(request, *args, **kwargs)


@chain_with(RegistrationRequiredMixin)
class PolicyRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not self.registration.agrees_to_policy:
            return redirect("register_policy")
        return super().dispatch(request, *args, **kwargs)


@chain_with(PolicyRequiredMixin)
class CreateOrderMixin:
    def dispatch(self, request, *args, **kwargs):
        self.order, created = Order.objects.update_or_create(
            registration=self.registration,
            session__isnull=False, 
            defaults={'session': Session.objects.get(pk=request.session.session_key)})
        return super().dispatch(request, *args, **kwargs)

@chain_with(PolicyRequiredMixin)
class OrderRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        try:
            self.order = Order.objects.get(registration=self.registration, session__pk=request.session.session_key)
        except ObjectDoesNotExist:
            return redirect('order')
        return super().dispatch(request, *args, **kwargs)


@chain_with(OrderRequiredMixin)
class NonZeroOrderRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not self.order.orderitem_set.exists():
            return redirect('make_payment')
        return super().dispatch(request, *args, **kwargs)


@chain_with(NonZeroOrderRequiredMixin)
class VolunteerSelectionRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if self.registration.wants_to_volunteer is None:
            return redirect('register_volunteer')
        return super().dispatch(request, *args, **kwargs)


@chain_with(VolunteerSelectionRequiredMixin)
class InvoiceRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if self.order.invoice_set.exists():
            return super().dispatch(request, *args, **kwargs)
        messages.error(request, 'You have no invoices to pay.')    
        return redirect('make_payment')


@chain_with(InvoiceRequiredMixin)
class FinishedOrderRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if self.order.accessible_price + self.order.donation == 0:
            return super().dispatch(request, *args, **kwargs)
        try:
            session_id = request.GET.get('session_id', '')
            total_amount = get_stripe_checkout_session_total(session_id)
            payment = Payment.objects.create(amount=total_amount, registration=self.registration, stripe_session_id=session_id)
            return super().dispatch(request, *args, **kwargs)
        except:
            return redirect('make_payment')


# This Mixin injects arbitrary dispatch code wherever it exists in the MRO. Just
# implement the dispatch_mixin() method in your class and it will be executed as
# if it was defined as a dispatch  Mixin. The only difference is that
# super().dispatch() should not be called at the end of dispatch_mixin() as this
# is handled by DispatchMixin.
class DispatchMixin:
    def dispatch(self, request, *args, **kwargs):
        r = self.dispatch_mixin(request)
        return r if r is not None else super().dispatch(request, *args, **kwargs)


# Use a CBV as an FBV: Overrides dispatch method of CBV with fbv() method.
# Implement the fbv() method as you would a normal FBV.
# This class should be added just before the View class in the inheritance sequence.
# You get the benefit of dispatch() mixins, class/instance variables, and inheritance,
# with the simplicity of FBVs.
# Recommended: Use with the TemplateView and manually call super().get(request)
# instead of render(). This provides useful context for free and let's you set
# template as a class variable.
class FunctionBasedView:
    def dispatch(self, request, *args, **kwargs):
        return self.fbv(request)
