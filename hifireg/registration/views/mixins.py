from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.shortcuts import redirect

from registration.models import Registration, Order, Payment, Event

from .stripe_helpers import get_stripe_checkout_session_total


# A magical decorator that provides syntactic cleanliness for chaining dispatch
# mixins. It replaces "this_class" with an empty class that inherits first from
# "base_class" and then from "this_class".
def chain_with(base_class):
    def chainer(this_class):
        return type(this_class.__name__, (base_class, this_class), {})
    return chainer


@chain_with(LoginRequiredMixin)
class EventRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        try:
            if (kwargs.get('event_slug') is not None):
                request.session['event_slug'] = kwargs.get('event_slug')
                self.event = Event.objects.get(slug=kwargs.get('event_slug'))
            else:
                self.event = Event.objects.get(slug=request.session['event_slug'])
        except:
            return redirect('event_selection')
        return super().dispatch(request, *args, **kwargs)

@chain_with(EventRequiredMixin)
class VaccinationRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if (self.event.requires_vaccination and not request.user.covid_vaccine_picture):  
            return redirect('index')
        return super().dispatch(request, *args, **kwargs)

@chain_with(VaccinationRequiredMixin)
class RegistrationRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        try:
            self.registration = Registration.objects.get(user=request.user, event=self.event)
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
class FormsRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if self.registration.wants_to_volunteer is None:
            return redirect('register_forms')
        return super().dispatch(request, *args, **kwargs)


@chain_with(FormsRequiredMixin)
class OrderRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                self.order = self.registration.order_set.select_for_update().get(session__isnull=False)
                self.order.session = Session.objects.get(session_key=request.session.session_key)
                self.order.save()
        except ObjectDoesNotExist:
            return redirect('register_products')
        return super().dispatch(request, *args, **kwargs)


@chain_with(OrderRequiredMixin)
class NonEmptyOrderRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not self.order.orderitem_set.exists():
            messages.error(request, 'You must add something to your cart before continuing.')
            return redirect('register_products')
        return super().dispatch(request, *args, **kwargs)

@chain_with(NonEmptyOrderRequiredMixin)
class NonZeroOrderRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if self.order.accessible_price + self.order.donation == 0:
            return redirect('index')
        return super().dispatch(request, *args, **kwargs)


@chain_with(NonEmptyOrderRequiredMixin)
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
            return redirect('payment_preview')


# This Mixin injects arbitrary dispatch code wherever it exists in the MRO. Just
# implement the dispatch_mixin() method in your class and it will be executed as
# if it was defined as a dispatch  Mixin. The only difference is that
# super().dispatch() should not be called at the end of dispatch_mixin() as this
# is handled by DispatchMixin.
class DispatchMixin:
    def dispatch(self, request, *args, **kwargs):
        r = self.dispatch_mixin(request)
        return r if r is not None else super().dispatch(request, *args, **kwargs)
