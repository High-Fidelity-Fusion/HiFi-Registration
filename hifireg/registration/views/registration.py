from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.views import View

from registration.forms import RegCompCodeForm, RegPolicyForm, RegDonateForm, RegVolunteerForm, RegVolunteerDetailsForm, RegMiscForm, RegAccessiblePriceCalcForm
from registration.models import CompCode, Order, ProductCategory, Registration, Volunteer, Product, APFund

from .mixins import RegistrationRequiredMixin, OrderRequiredMixin, FunctionBasedView
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
        product = Product.objects.get(pk=request.GET.get('product', None))
        success = Order.for_user(request.user).add_item(product, int(request.GET.get('increment', None)))
        product = Product.objects.get_product_info_for_user(request.user).get(pk=product.pk)

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
        product = Product.objects.get(pk=request.GET.get('product', None))
        Order.for_user(request.user).remove_item(product, int(request.GET.get('decrement', None)))
        product = Product.objects.get_product_info_for_user(request.user).get(pk=product.pk)

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


class RegisterSubtotal(LoginRequiredMixin, RegistrationRequiredMixin, OrderRequiredMixin, TemplateView):
    template_name = "registration/register_subtotal.html"
    previous_button = LinkButton("register_merchandise", "Previous")
    ap_yes_button = SubmitButton("claim_ap")
    ap_no_button = LinkButton("register_donate")

    def get(self, request):
        self.ap_available = self.order.ap_eligible_amount <= APFund.get_available_funds()
        return super().get(request)

    def post(self, request):
        if "claim_ap" in request.POST:
            if self.order.claim_accessible_pricing():
                return redirect("register_accessible_pricing")
            else:
                self.ap_available = False
                return super().get(request)


class RegisterAP(LoginRequiredMixin, RegistrationRequiredMixin, OrderRequiredMixin, TemplateView):
    template_name = "registration/register_accessible_pricing2.html"
    previous_button = LinkButton("register_subtotal", "Previous")
    next_button = LinkButton("register_volunteer", "Next")

    def post(self, request):
        price = request.POST.get('price_submit', self.order.original_price)
        self.order.accessible_price = price
        self.order.save()
        return redirect('register_volunteer')


@must_have_registration  #TODO change to must_have_order when orders are working
def register_accessible_pricing(request):
    # TODO make function dependent on order, uncomment order-dependent-code
    # order = Order.objects.get(session=request.session)
    original_price = 225
    ap_eligible_amount = 200
    if request.method == 'POST':
        if 'previous' in request.POST:
            return redirect('register_subtotal')
        form = RegAccessiblePriceCalcForm(original_price, ap_eligible_amount, request.POST,)
        if form.is_valid():
            cd = form.cleaned_data
            print(cd)
            # order.accessible_price = form.cleaned_data[accessible_price]
            # order.stretch_price = form.cleaned_data[stretch_price]
            # order.save()

            return redirect('register_volunteer')

    else:
        form = RegAccessiblePriceCalcForm(original_price, ap_eligible_amount)
        # if order.accessible_price != order.original_price:
        # for field in form:
        #     if '$' in field.label:
        #         if int(field.label[1]) >= order.accessible_price:
        #           field.value = 1
        #         elif int(field.label[1]) >= order.stretch_price:
        #           field.value = 2
        #         else:
        #           field.value = 3
    return render(request, 'registration/register_accessible_pricing.html', {'form': form})


@must_have_registration  # change to must_have_order when orders are working
def register_donate(request):
    form = RegDonateForm
    if request.method == 'POST':
        if 'previous' in request.POST:
            return redirect('register_subtotal')
        return redirect('register_volunteer')
    return render(request, 'registration/register_donate.html', {'form': form})


@must_have_registration  # change to must_have_order when orders are working
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


@must_have_registration  # change to must_have_order when orders are working
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


@must_have_registration  # change to must_have_order when orders are working
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


@must_have_registration  # change to must_have_order when orders are working
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
