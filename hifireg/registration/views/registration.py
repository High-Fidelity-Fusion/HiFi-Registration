from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.views import View

from registration.forms import RegCompCodeForm, RegPolicyForm, RegDonateForm, RegVolunteerForm, RegVolunteerDetailsForm, RegMiscForm
from registration.models import CompCode, Order, ProductCategory, Registration, Volunteer, Product, APFund

from .mixins import RegistrationRequiredMixin, OrderRequiredMixin, NonZeroOrderRequiredMixin
from .mixins import DispatchMixin, FunctionBasedView
from .utils import SubmitButton, LinkButton
from .helpers import get_context_for_product_selection
from .decorators import must_have_registration, must_have_active_order, must_have_active_order_and_dance_pass


class Index(LoginRequiredMixin, FunctionBasedView, View):
    def fbv(self, request):
        return render(request, 'registration/index.html', {'user': request.user})


@login_required
def register_comp_code(request):
    try:
        registration = Registration.objects.get(user=request.user)
    except ObjectDoesNotExist:
        registration = Registration(user=request.user)
        registration.save()

    next_page = 'register_policy'

    # Skip condition
    if registration.comp_code is not None:
        return redirect(next_page)

    if request.method == 'POST':
        if 'previous' in request.POST:
            return redirect('index')

        form = RegCompCodeForm(request.POST)

        with transaction.atomic():
            CompCode.objects.select_for_update()
            if form.is_valid():
                if form.cleaned_data.get('code'):
                    registration.comp_code = CompCode.objects.get(code=form.cleaned_data.get('code'))
                    registration.order_set.filter(session__isnull=False).delete()
                    registration.save()
                return redirect(next_page)

    else:
        form = RegCompCodeForm(initial={'code': registration.comp_code.code if registration.comp_code else ''})
    return render(request, 'registration/register_comp_code.html', {'form': form})


@must_have_registration
def register_policy(request):
    if request.method == 'POST':
        if 'previous' in request.POST:
            return redirect('register_comp_code')
        form = RegPolicyForm(request.POST, instance=Registration.objects.get(user=request.user))
        if form.is_valid():
            form.save()
            return redirect('register_ticket_selection')
    else:
        form = RegPolicyForm(instance=Registration.objects.get(user=request.user))
    return render(request, 'registration/register_policy.html', {'form': form})


def add_item(request):
    try:
        product_id = request.GET.get('product', None)
        success = Order.for_user(request.user).add_item(product_id, int(request.GET.get('increment', None)))

        data = {
            'success': success,
        }
    except Exception as e:
        data = {
            'error': "error: {0}".format(e)
        }
    return JsonResponse(data)


def remove_item(request):
    try:
        product_id = request.GET.get('product', None)
        Order.for_user(request.user).remove_item(product_id, int(request.GET.get('decrement', None)))

        data = {}
    except Exception as e:
        data = {
            'error': "{0}".format(e)
        }
    return JsonResponse(data)


@must_have_registration
def register_ticket_selection(request):
    if request.method == 'POST':
        if 'previous' in request.POST:
            return redirect('register_policy')
        return redirect('register_class_selection')

    order, created = Order.objects.update_or_create(registration=request.user.registration_set.get(), session__isnull=False, defaults={'session': Session.objects.get(pk=request.session.session_key)})

    context = get_context_for_product_selection(ProductCategory.DANCE, request.user)

    return render(request, 'registration/register_selection.html', context)


@must_have_active_order
def register_class_selection(request):
    if request.method == 'POST':
        if 'previous' in request.POST:
            return redirect('register_ticket_selection')
        return redirect('register_showcase')

    context = get_context_for_product_selection(ProductCategory.CLASS, request.user)

    return render(request, 'registration/register_selection.html', context)


@must_have_active_order
def register_showcase(request):
    if request.method == 'POST':
        if 'previous' in request.POST:
            return redirect('register_class_selection')
        return redirect('register_merchandise')

    order, created = Order.objects.update_or_create(registration=request.user.registration_set.get(), session__isnull=False, defaults={'session': Session.objects.get(pk=request.session.session_key)})

    context = get_context_for_product_selection(ProductCategory.SHOWCASE, request.user)

    return render(request, 'registration/register_selection.html', context)


@must_have_active_order
def register_merchandise(request):
    if request.method == 'POST':
        if 'previous' in request.POST:
            return redirect('register_showcase')
        return redirect('register_subtotal')

    context = get_context_for_product_selection(ProductCategory.MERCH, request.user)

    return render(request, 'registration/register_selection.html', context)


class RegisterSubtotal(NonZeroOrderRequiredMixin, TemplateView):
    template_name = "registration/register_subtotal.html"
    previous_button = LinkButton("register_merchandise", "Previous")
    ap_yes_button = SubmitButton("claim_ap")
    ap_no_button = LinkButton("register_donate")

    def get(self, request):
        self.ap_available = self.order.ap_eligible_amount <= self.order.get_available_ap_funds()
        return super().get(request)

    def post(self, request):
        if "claim_ap" in request.POST:
            if self.order.claim_accessible_pricing():
                return redirect("register_accessible_pricing")
            else:
                self.ap_available = False
                return super().get(request)


class RegisterAP(NonZeroOrderRequiredMixin, DispatchMixin, TemplateView):
    template_name = "registration/register_accessible_pricing.html"
    previous_button = LinkButton("register_subtotal", "Previous")
    next_button = LinkButton("register_volunteer", "Next")

    def dispatch_mixin(self, request):
        if not self.order.is_accessible_pricing:
            return redirect('register_subtotal')

    def post(self, request):
        price = int(request.POST.get('price_submit', self.order.original_price))
        if price <  self.order.original_price - self.order.ap_eligible_amount:
            raise SuspiciousOperation('Your price cannot be reduced by more than the AP eligible amount.')
            #TODO: should this validation be in Order model?
        self.order.accessible_price = price
        self.order.save()
        return redirect('register_volunteer')


@must_have_active_order
def register_donate(request):
    order = Order.for_user(request.user)

    if request.method == 'POST':
        if 'previous' in request.POST:
            return redirect('register_subtotal')
        form = RegDonateForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            order.accessible_price = order.original_price + int(100*cd['donation'])
            order.save()
            return redirect('register_volunteer')
    else:
        subtotal = '${:,.2f}'.format(order.original_price * .01)
        if order.accessible_price > order.original_price:
            donation = order.accessible_price - order.original_price
        else:
            donation = 0
        form = RegDonateForm()
        form.fields['donation'].initial = float(donation) * .01
        context = {'form': form, 'subtotal': subtotal, 'donation': donation}
    return render(request, 'registration/register_donate.html', context)


@must_have_registration
def register_volunteer(request):
    if request.method == 'POST':
        if 'previous' in request.POST:
            if True:  # redirect based need for accessible pricing
                return redirect('register_donate')
            else:
                return redirect('register_accessible_pricing')
        form = RegVolunteerForm(request.POST, instance=Registration.objects.get(user=request.user))
        if form.is_valid():
            registration = form.save()
            if registration.wants_to_volunteer:
                return redirect('register_volunteer_details')
            else:
                return redirect('register_misc')
    else:
        form = RegVolunteerForm(instance=Registration.objects.get(user=request.user))
    return render(request, 'registration/register_volunteer.html', {'form': form})


@must_have_registration
def register_volunteer_details(request):
    registration = Registration.objects.get(user=request.user)
    try:
        volunteer = Volunteer.objects.get(registration=registration)
    except ObjectDoesNotExist:
        volunteer = Volunteer()
        volunteer.save()
        volunteer.registration = registration
        volunteer.save()

    if request.method == 'POST':
        if 'previous' in request.POST:
            return redirect('register_volunteer')
        form = RegVolunteerDetailsForm(request.POST, request.FILES, instance=volunteer)
        if form.is_valid():
            form.save()
            return redirect('register_misc')
    else:
        form = RegVolunteerDetailsForm(instance=volunteer)
    return render(request, 'registration/register_volunteer_details.html', {'form': form})


@must_have_registration
def register_misc(request):
    if request.method == 'POST':
        registration = Registration.objects.get(user=request.user)
        if 'previous' in request.POST:
            if registration.wants_to_volunteer:
                return redirect('register_volunteer_details')
            else:
                return redirect('register_volunteer')
        form = RegMiscForm(request.POST, instance=registration)
        if form.is_valid():
            form.save()
            return redirect('payment')  # logic needed here to decide whether payment is needed
    else:
        form = RegMiscForm(instance=Registration.objects.get(user=request.user))
    return render(request, 'registration/register_misc.html', {'form': form})


@must_have_registration
def make_payment(request):
    form = None
    if request.method == 'POST':
        if 'previous' in request.POST:
            return redirect('register_misc')
        return redirect('payment_confirmation')
    else:
        return render(request, 'registration/payment.html', {'form': form})


def payment_confirmation(request):
    return render(request, 'registration/payment_confirmation.html', {})

def hello_world(request):
    return render(request, 'registration/base.html', {})