from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic.base import TemplateView
from django.views import View
from datetime import datetime, timedelta

import stripe

from registration.forms import RegCompCodeForm, RegPolicyForm, RegDonateForm, RegVolunteerForm, RegVolunteerDetailsForm, RegMiscForm
from registration.models import CompCode, Order, ProductCategory, Registration, Volunteer, Product, APFund, Invoice, Payment

from .mixins import RegistrationRequiredMixin, OrderRequiredMixin, NonZeroOrderRequiredMixin, PolicyRequiredMixin, VolunteerSelectionRequiredMixin, InvoiceRequiredMixin
from .mixins import DispatchMixin, FunctionBasedView
from .utils import SubmitButton, LinkButton
from .helpers import get_context_for_product_selection


class IndexView(LoginRequiredMixin, TemplateView):
    register_button = LinkButton("register_comp_code", "Register")
    account_button = LinkButton("view_user", "Account")
    template_name = "registration/index.html"


class RegisterCompCodeView(LoginRequiredMixin, FunctionBasedView, View):
    def fbv(self, request):
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


class RegisterPolicyView(RegistrationRequiredMixin, FunctionBasedView, View):
    def fbv(self, request):       
        if request.method == 'POST':
            if 'previous' in request.POST:
                return redirect('register_comp_code')
            form = RegPolicyForm(request.POST, instance=self.registration)
            if form.is_valid():
                form.save()
                return redirect('register_ticket_selection')
        else:
            form = RegPolicyForm(instance=self.registration)
        return render(request, 'registration/register_policy.html', {'form': form})


class AddItemView(FunctionBasedView, View):
    def fbv(self, request):
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


class RemoveItemView(FunctionBasedView, View):
    def fbv(self, request):
        try:
            product_id = request.GET.get('product', None)
            Order.for_user(request.user).remove_item(product_id, int(request.GET.get('decrement', None)))

            data = {}
        except Exception as e:
            data = {
                'error': "{0}".format(e)
            }
        return JsonResponse(data)


class RegisterTicketSelectionView(PolicyRequiredMixin, DispatchMixin, TemplateView):
    template_name = 'registration/register_selection.html'
    previous_button = LinkButton("register_policy", "Previous")
    next_button = LinkButton("register_class_selection", "Next")

    def dispatch_mixin(self, request):
        order, created = Order.objects.update_or_create(
            registration=request.user.registration_set.get(), 
            session__isnull=False, 
            defaults={'session': Session.objects.get(pk=request.session.session_key)})

        self.extra_context = get_context_for_product_selection(ProductCategory.DANCE, request.user)


class RegisterClassSelectionView(OrderRequiredMixin, DispatchMixin, TemplateView):
    template_name = 'registration/register_selection.html'
    previous_button = LinkButton("register_ticket_selection", "Previous")
    next_button = LinkButton("register_showcase", "Next")

    def dispatch_mixin(self, request):
        self.extra_context = get_context_for_product_selection(ProductCategory.CLASS, request.user)


class RegisterShowcaseView(OrderRequiredMixin, DispatchMixin, TemplateView):
    template_name = 'registration/register_selection.html'
    previous_button = LinkButton("register_class_selection", "Previous")
    next_button = LinkButton("register_merchandise", "Next")

    def dispatch_mixin(self, request):
        self.extra_context = get_context_for_product_selection(ProductCategory.SHOWCASE, request.user)


class RegisterMerchandiseView(OrderRequiredMixin, DispatchMixin, TemplateView):
    template_name = 'registration/register_selection.html'
    previous_button = LinkButton("register_showcase", "Previous")
    next_button = LinkButton("register_subtotal", "Next")

    def dispatch_mixin(self, request):
        self.extra_context = get_context_for_product_selection(ProductCategory.MERCH, request.user)


class RegisterSubtotal(NonZeroOrderRequiredMixin, TemplateView):
    template_name = "registration/register_subtotal.html"
    previous_button = LinkButton("register_merchandise", "Previous")
    ap_yes_button = SubmitButton("claim_ap")
    ap_no_button = LinkButton("register_donate")

    def get(self, request):
        self.ap_available = self.order.ap_eligible_amount <= self.order.get_available_ap_funds()
        return super().get(request)

    def post(self, request):
        if self.ap_yes_button.name in request.POST:
            if self.order.claim_accessible_pricing():
                return redirect("register_accessible_pricing")
            else:
                self.ap_available = False
                return super().get(request)


class RegisterAccessiblePricingView(NonZeroOrderRequiredMixin, DispatchMixin, TemplateView):
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


class RegisterDonateView(NonZeroOrderRequiredMixin, FunctionBasedView, View):
    def fbv(self, request):
        order = Order.for_user(request.user)

        if request.method == 'POST':
            if 'previous' in request.POST:
                return redirect('register_subtotal')
            form = RegDonateForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                order.donation = int(100 * cd['donation'])
                order.save()
                return redirect('register_volunteer')
        else:
            subtotal = '${:,.2f}'.format(order.original_price * .01)
            form = RegDonateForm()
            form.fields['donation'].initial = float(order.donation) * .01
            context = {'form': form, 'subtotal': subtotal, 'donation': order.donation}
        return render(request, 'registration/register_donate.html', context)


class RegisterVolunteerView(NonZeroOrderRequiredMixin, FunctionBasedView, View):
    def fbv(self, request):
        if request.method == 'POST':
            if 'previous' in request.POST:
                if True:  # redirect based need for accessible pricing
                    return redirect('register_donate')
                else:
                    return redirect('register_accessible_pricing')
            form = RegVolunteerForm(request.POST, instance=self.registration)
            if form.is_valid():
                registration = form.save()
                if registration.wants_to_volunteer:
                    return redirect('register_volunteer_details')
                else:
                    return redirect('register_misc')
        else:
            form = RegVolunteerForm(instance=self.registration)
        return render(request, 'registration/register_volunteer.html', {'form': form})


class RegisterVolunteerDetailsView(VolunteerSelectionRequiredMixin, FunctionBasedView, View):
    def fbv(self, request):
        registration = self.registration
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


class RegisterMiscView(VolunteerSelectionRequiredMixin, FunctionBasedView, View):
    def fbv(self, request):
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
                return redirect('payment_plan')  # logic needed here to decide whether payment is needed
        else:
            form = RegMiscForm(instance=self.registration)
        return render(request, 'registration/register_misc.html', {'form': form})


class PaymentPlan(VolunteerSelectionRequiredMixin, TemplateView):
    template_name = 'registration/payment_plan.html'
    previous_button = LinkButton("register_misc", "Previous")
    next_button = SubmitButton("make_payment", "Next")

    def get(self, request):
        return super().get(request)

    def post(self, request):
        if self.next_button.name in request.POST:
            Invoice.objects.filter(order=self.order).delete()
            Invoice.objects.create(order=self.order, pay_at_checkout=True, amount=12300)
            Invoice.objects.create(order=self.order, due_date=datetime.now()+timedelta(weeks=2), amount=12300)
            Invoice.objects.create(order=self.order, due_date=datetime.now()+timedelta(weeks=4), amount=12300)
            Invoice.objects.create(order=self.order, due_date=datetime.now()+timedelta(weeks=6), amount=12300)
            return redirect('make_payment')



class MakePaymentView(InvoiceRequiredMixin, TemplateView):
    template_name = 'registration/payment.html'
    previous_button = LinkButton("payment_plan", "Previous")

    def post(self, request):
        if 'previous' in request.POST:
            return redirect('payment_plan')

    def get(self, request):
        self.items = self.order.orderitem_set.order_by('product__category__section', 'product__category__rank', 'product__slots__rank').iterator()
        return super().get(request)


class NewCheckoutView(InvoiceRequiredMixin, FunctionBasedView, View):
    def fbv(self, request):
        if request.method == 'GET':
            # configure Stripe w/secret API key
            stripe.api_key = settings.STRIPE_SECRET_TEST_KEY

            # Using fake amount and variable because real variable unknown atm 6.15.20
            invoice = self.order.invoice_set.get(pay_at_checkout=True)
            reg_amount = invoice.amount

            # urls for recieving redirects from Stripe
            success_url = request.build_absolute_uri(reverse('payment_confirmation')) + '?session_id={CHECKOUT_SESSION_ID}'
            cancel_url = request.build_absolute_uri(reverse('make_payment'))
      
            try:
                # Create new Checkout Session for the order
                # Other optional params: https:#stripe.com/docs/api/checkout/sessions/create
                checkout_session = stripe.checkout.Session.create(
                    success_url = success_url,
                    cancel_url = cancel_url,
                    payment_method_types = ['card'],
                    line_items = [{
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': 'HiFi Registration',
                            },
                            'unit_amount': reg_amount,
                        },
                        'quantity': 1,
                    }],
                    mode = 'payment',
                )
                # Provide public key to initialize Stripe Client in browser
                # And checkout session id
                return JsonResponse({
                    'public_key': settings.STRIPE_PUBLIC_TEST_KEY,
                    'session_id': checkout_session['id'],
                })
            except Exception as e:
                return JsonResponse({'error': str(e)})


class PaymentConfirmationView(OrderRequiredMixin, FunctionBasedView, View):
    def fbv(self, request):
<<<<<<< HEAD
        session_id = request.GET.get('session_id', '')
        # If user refreshes it will not throw the ugly IntegrityError page
        try: 
            payment = Payment.objects.get(stripe_session_id=session_id)
        except ObjectDoesNotExist:
            stripe.api_key = settings.STRIPE_SECRET_TEST_KEY
            line_items = stripe.checkout.Session.list_line_items(session_id)
            total_amount = 0
            for line_item in line_items['data']:
                total_amount += line_item['amount_total']
            payment = Payment.objects.create(amount=total_amount, registration=self.registration, stripe_session_id=session_id)
        
        self.order.session = None
        self.order.save()
        
        return render(request, 'registration/payment_confirmation.html', {
            'payment': payment
        })
=======
        return render(request, 'registration/payment_confirmation.html', {})


class VolunteerEdit(LoginRequiredMixin, RegistrationRequiredMixin, TemplateView):
    template_name = "registration/volunteer_edit.html"

    def get(self, request):
        return super().get(request)

    # def post(self, request):
>>>>>>> Got volunteer edit page added and routed, no content yet.
