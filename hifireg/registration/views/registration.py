from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.views import View
from datetime import datetime, timedelta

from registration.forms import BetaPasswordForm, RegCompCodeForm, RegPolicyForm, RegDonateForm, RegVolunteerForm, RegVolunteerDetailsForm, RegMiscForm

from registration.models import CompCode, Order, ProductCategory, Registration, Volunteer, Product, APFund, Invoice, Payment, OrderItem
from registration.models.helpers import with_is_paid

from .mixins import RegistrationRequiredMixin, OrderRequiredMixin, NonZeroOrderRequiredMixin, PolicyRequiredMixin, VolunteerSelectionRequiredMixin, InvoiceRequiredMixin
from .mixins import DispatchMixin, FunctionBasedView
from .utils import SubmitButton, LinkButton
from .helpers import get_context_for_product_selection
from .stripe_helpers import create_stripe_checkout_session, get_stripe_checkout_session_total
from .mailchimp_client import create_or_update_subscriber


class BetaLoginView(FormView):
    template_name = 'registration/beta_login.html'
    form_class = BetaPasswordForm
    success_url = '/'

    def form_valid(self, form):
        self.request.session['site_password'] = True
        return super().form_valid(form)


class IndexView(LoginRequiredMixin, TemplateView):
    register_button = LinkButton('register_comp_code', 'Register')
    account_button = LinkButton('view_user', 'Account')
    invoices_button = LinkButton('invoices', 'Pay Other Invoices')
    template_name = 'registration/index.html'

    def get(self, request):
        self.items = OrderItem.objects.filter(order__registration__user=request.user).order_by('product__category__section', 'product__category__rank', 'product__slots__rank').iterator()
        return super().get(request)

class OrdersView(LoginRequiredMixin, TemplateView):
    template_name = 'registration/orders.html'

    def get(self, request):
        self.orders = [{
            'order': order,
            'items': order.orderitem_set.order_by('product__category__section', 'product__category__rank', 'product__slots__rank').iterator()
        } for order in Order.objects.filter(registration__user=request.user, session__isnull=True).order_by('-pk').iterator()]
        return super().get(request)


class InvoicesView(RegistrationRequiredMixin, FunctionBasedView, View):
    def fbv(self, request):
        unpaid_invoices = with_is_paid(
            Invoice.objects.filter(
                order__registration__pk=self.registration.pk
            ).order_by('due_date')
        ).filter(is_paid=False)
        
        return render(request, 'registration/invoices.html', {
            'unpaid_invoices': unpaid_invoices,
            'amount_paid': int(request.GET.get('amount_paid', '0')),
        })


class PayInvoicesView(RegistrationRequiredMixin, FunctionBasedView, View):
    def fbv(self, request):
        if request.method == 'GET':

            invoices_amount = request.GET.get('amount', '')

            # urls for recieving redirects from Stripe
            success_url = request.build_absolute_uri(reverse('pay_success')) + '?session_id={CHECKOUT_SESSION_ID}'
            cancel_url = request.build_absolute_uri(reverse('invoices'))
      
            try:
                checkout_session_id = create_stripe_checkout_session(invoices_amount, success_url, cancel_url)
                # Provide public key to initialize Stripe Client in browser
                # And checkout session id
                return JsonResponse({
                    'public_key': settings.STRIPE_PUBLIC_TEST_KEY,
                    'session_id': checkout_session_id,
                })
            except Exception as e:
                return JsonResponse({'error': str(e)})


class PayInvoicesSuccessView(RegistrationRequiredMixin, FunctionBasedView, View):
    def fbv(self, request):
        session_id = request.GET.get('session_id', '')
        # If user refreshes it will not throw the ugly IntegrityError page
        try: 
            payment = Payment.objects.get(stripe_session_id=session_id)
        except ObjectDoesNotExist:
            total_amount = get_stripe_checkout_session_total(session_id)
            payment = Payment.objects.create(amount=total_amount, registration=self.registration, stripe_session_id=session_id)
        
        return redirect(reverse('invoices') + '?amount_paid=' + str(payment.amount))


class RegisterCompCodeView(LoginRequiredMixin, FunctionBasedView, View):
    def fbv(self, request):
        try:
            registration = Registration.objects.get(user=request.user)
        except ObjectDoesNotExist:
            registration = Registration(user=request.user)
            registration.save()

        # Skip condition
        if registration.comp_code is not None:
            if registration.is_submitted:
                return redirect('register_ticket_selection')
            else:
                return redirect('register_policy')

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

                    if registration.is_submitted:
                        return redirect('register_ticket_selection')
                    else:
                        return redirect('register_policy')

        else:
            form = RegCompCodeForm(initial={'code': registration.comp_code.code if registration.comp_code else ''})
        return render(request, 'registration/register_comp_code.html', {'form': form})


class RegisterPolicyView(RegistrationRequiredMixin, FunctionBasedView, View):
    def fbv(self, request):
        if request.method == 'POST':
            if 'previous' in request.POST:
                if self.registration.comp_code is None:
                    return redirect('register_comp_code')
                else:
                    return redirect('index')
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
                'error': 'error: {0}'.format(e)
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
                'error': '{0}'.format(e)
            }
        return JsonResponse(data)


class RegisterTicketSelectionView(PolicyRequiredMixin, DispatchMixin, TemplateView):
    template_name = 'registration/register_selection.html'
    previous_button = SubmitButton('Previous')
    next_button = LinkButton('register_class_selection', 'Next')

    def dispatch_mixin(self, request):
        order, created = Order.objects.update_or_create(
            registration=self.registration,
            session__isnull=False, 
            defaults={'session': Session.objects.get(pk=request.session.session_key)})

        self.extra_context = get_context_for_product_selection(ProductCategory.DANCE, request.user)

    def post(self, request):
        if self.previous_button.name in request.POST:
            if self.registration.is_submitted:
                if self.registration.comp_code is None:
                    return redirect('register_comp_code')
                else:
                    return redirect('index')
            else:
                return redirect('register_policy')



class RegisterClassSelectionView(OrderRequiredMixin, DispatchMixin, TemplateView):
    template_name = 'registration/register_selection.html'
    previous_button = LinkButton('register_ticket_selection', 'Previous')
    next_button = LinkButton('register_showcase', 'Next')

    def dispatch_mixin(self, request):
        self.extra_context = get_context_for_product_selection(ProductCategory.CLASS, request.user)


class RegisterShowcaseView(OrderRequiredMixin, DispatchMixin, TemplateView):
    template_name = 'registration/register_selection.html'
    previous_button = LinkButton('register_class_selection', 'Previous')
    next_button = LinkButton('register_merchandise', 'Next')

    def dispatch_mixin(self, request):
        self.extra_context = get_context_for_product_selection(ProductCategory.SHOWCASE, request.user)


class RegisterMerchandiseView(OrderRequiredMixin, DispatchMixin, TemplateView):
    template_name = 'registration/register_selection.html'
    previous_button = LinkButton('register_showcase', 'Previous')
    next_button = LinkButton('register_subtotal', 'Next')

    def dispatch_mixin(self, request):
        self.extra_context = get_context_for_product_selection(ProductCategory.MERCH, request.user)


class RegisterSubtotal(NonZeroOrderRequiredMixin, TemplateView):
    template_name = 'registration/register_subtotal.html'
    previous_button = LinkButton('register_merchandise', 'Previous')
    ap_yes_button = SubmitButton('claim_ap')
    ap_no_button = SubmitButton('not_ap')

    def get(self, request):
        if self.order.ap_eligible_amount == 0:
            return redirect('register_donate')
        self.ap_available = self.order.ap_eligible_amount <= self.order.get_available_ap_funds() or self.order.is_accessible_pricing
        self.ineligible_items = self.order.orderitem_set.filter(unit_price__gt=0, product__is_ap_eligible=False).order_by('product__category__section', 'product__category__rank', 'product__slots__rank')
        return super().get(request)

    def post(self, request):
        if self.ap_yes_button.name in request.POST:
            if self.order.is_accessible_pricing or self.order.claim_accessible_pricing():
                return redirect('register_accessible_pricing')
            else:
                self.ap_available = False
                return super().get(request)
        elif self.ap_no_button.name in request.POST:
            self.order.revoke_accessible_pricing()
            return redirect('register_donate')


class RegisterAccessiblePricingView(NonZeroOrderRequiredMixin, DispatchMixin, TemplateView):
    template_name = 'registration/register_accessible_pricing.html'
    previous_button = LinkButton('register_subtotal', 'Previous')

    def dispatch_mixin(self, request):
        if not self.order.is_accessible_pricing:
            return redirect('register_subtotal')

    def post(self, request):
        price = int(request.POST.get('price_submit', self.order.original_price))
        self.order.set_accessible_price(price)
        if self.registration.is_submitted:
            return redirect('payment_plan')
        else:
            return redirect('register_volunteer')


class RegisterDonateView(NonZeroOrderRequiredMixin, DispatchMixin, FunctionBasedView, View):
    def dispatch_mixin(self, request):
        if self.order.is_accessible_pricing:
            return redirect('register_subtotal')

    def fbv(self, request):
        order = Order.for_user(request.user)

        if request.method == 'POST':
            if 'previous' in request.POST:
                if self.order.ap_eligible_amount == 0:
                    return redirect('register_merchandise')
                return redirect('register_subtotal')
            form = RegDonateForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                order.donation = int(100 * cd['donation'])
                order.save()
                if self.registration.is_submitted:
                    return redirect('payment_plan')
                else:
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
                if self.order.is_accessible_pricing:
                    return redirect('register_subtotal')
                else:
                    return redirect('register_donate')
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
    previous_button = SubmitButton('Previous')
    next_button = SubmitButton('Next')

    def get(self, request):
        if self.order.accessible_price + self.order.donation == 0:
            self.order.session = None
            self.order.save()
            create_or_update_subscriber(request.user, self.registration)
            return render(request, 'registration/payment_confirmation.html', {})

        self.months = range(1, 5)
        return super().get(request)

    def post(self, request):
        if self.next_button.name in request.POST:
            Invoice.objects.filter(order=self.order).delete()
            Invoice.objects.create(order=self.order, pay_at_checkout=True, amount=12300)
            Invoice.objects.create(order=self.order, due_date=datetime.now()+timedelta(weeks=2), amount=12300)
            Invoice.objects.create(order=self.order, due_date=datetime.now()+timedelta(weeks=4), amount=12300)
            Invoice.objects.create(order=self.order, due_date=datetime.now()+timedelta(weeks=6), amount=12300)
            return redirect('make_payment')

        elif self.previous_button.name in request.POST:
            if self.registration.is_submitted:
                if self.order.is_accessible_pricing:
                    return redirect('register_subtotal')
                else:
                    return redirect('register_donate')
            else:
                return redirect('register_misc')


class MakePaymentView(InvoiceRequiredMixin, TemplateView):
    template_name = 'registration/payment.html'
    previous_button = LinkButton('payment_plan', 'Previous')

    def post(self, request):
        if 'previous' in request.POST:
            return redirect('payment_plan')

    def get(self, request):
        self.amount_due = self.order.invoice_set.get(pay_at_checkout=True).amount
        self.items = self.order.orderitem_set.order_by('product__category__section', 'product__category__rank', 'product__slots__rank').iterator()
        return super().get(request)



class NewCheckoutView(InvoiceRequiredMixin, FunctionBasedView, View):
    def fbv(self, request):
        if request.method == 'GET':

            # Using fake amount and variable because real variable unknown atm 6.15.20
            invoice = self.order.invoice_set.get(pay_at_checkout=True)
            reg_amount = invoice.amount

            # urls for recieving redirects from Stripe
            success_url = request.build_absolute_uri(reverse('payment_confirmation')) + '?session_id={CHECKOUT_SESSION_ID}'
            cancel_url = request.build_absolute_uri(reverse('make_payment'))
      
            try:
                checkout_session_id = create_stripe_checkout_session(reg_amount, success_url, cancel_url)
                
                # Provide public key to initialize Stripe Client in browser
                # And checkout session id
                return JsonResponse({
                    'public_key': settings.STRIPE_PUBLIC_TEST_KEY,
                    'session_id': checkout_session_id,
                })
            except Exception as e:
                return JsonResponse({'error': str(e)})


class PaymentConfirmationView(OrderRequiredMixin, FunctionBasedView, View):
    def fbv(self, request):
        session_id = request.GET.get('session_id', '')
        # If user refreshes it will not throw the ugly IntegrityError page
        try: 
            payment = Payment.objects.get(stripe_session_id=session_id)
        except ObjectDoesNotExist:
            total_amount = get_stripe_checkout_session_total(session_id)
            payment = Payment.objects.create(amount=total_amount, registration=self.registration, stripe_session_id=session_id)

        create_or_update_subscriber(request.user, self.registration)
        self.order.session = None
        self.order.save()
        
        return render(request, 'registration/payment_confirmation.html', {
            'payment': payment
        })


