from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView, UpdateView
from django.views import View
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from registration.forms import BetaPasswordForm, RegCompCodeForm, RegisterPolicyForm, RegisterDonateForm, RegVolunteerForm, RegVolunteerDetailsForm, RegMiscForm
from registration.models import CompCode, Order, ProductCategory, Registration, Volunteer, Product, APFund, Invoice, Payment, OrderItem
from registration.models.helpers import with_is_paid

from .email_handler import send_confirmation
from .helpers import get_context_for_product_selection, get_quantity_purchased_for_item, add_quantity_range_to_item, add_remove_item_view
from .mailchimp_client import create_or_update_subscriber
from .mixins import RegistrationRequiredMixin, OrderRequiredMixin, NonZeroOrderRequiredMixin, PolicyRequiredMixin, InvoiceRequiredMixin, FinishedOrderRequiredMixin, CreateOrderMixin
from .mixins import DispatchMixin
from .stripe_helpers import create_stripe_checkout_session, get_stripe_checkout_session_total
from .utils import SubmitButton, LinkButton


class BetaLoginView(FormView):
    template_name = 'registration/beta_login.html'
    form_class = BetaPasswordForm
    success_url = '/'

    def form_valid(self, form):
        self.request.session['site_password'] = True
        return super().form_valid(form)


class IndexView(LoginRequiredMixin, DispatchMixin, TemplateView):
    register_button = LinkButton('register_policy', 'Begin Registration')
    products_button = LinkButton('register_products', 'Purchase More')
    invoices_button = LinkButton('invoices', 'Make a Payment')
    template_name = 'registration/index.html'

    def dispatch_mixin(self, request):
        try:
            self.registration = Registration.objects.get(user=request.user)
        except ObjectDoesNotExist:
            self.registration = Registration(user=request.user)
            self.registration.save()

    def get(self, request):
        invoices = with_is_paid(Invoice.objects.filter(order__registration__user=request.user))
        if self.registration.is_submitted:
            self.items = OrderItem.objects.filter(order__registration__user=request.user).order_by('product__category__section', 'product__category__rank', 'product__slots__rank').iterator()
            self.is_payment_plan = invoices.count() > Order.objects.filter(registration__user=request.user, session__isnull=True).count()
            self.has_unpaid_invoice = invoices.filter(is_paid=False).exists()
            if self.has_unpaid_invoice:
                self.days_until_due = (invoices.filter(is_paid=False).first().due_date.date() - timezone.now().date()).days
        return super().get(request)


class OrdersView(LoginRequiredMixin, TemplateView):
    template_name = 'registration/orders.html'

    def get(self, request):
        self.orders = [{
            'order': order,
            'items': order.orderitem_set.order_by('product__category__section', 'product__category__rank', 'product__slots__rank').iterator()
        } for order in Order.objects.filter(registration__user=request.user, session__isnull=True).order_by('-pk').iterator()]
        return super().get(request)


class InvoicesView(RegistrationRequiredMixin, View):
    def get(self, request):
        unpaid_invoices = with_is_paid(
            Invoice.objects.filter(
                order__registration__pk=self.registration.pk
            )
        ).filter(is_paid=False)
        
        return render(request, 'registration/invoices.html', {
            'unpaid_invoices': unpaid_invoices,
            'amount_paid': int(request.GET.get('amount_paid', '0')),
        })


class PayInvoicesView(RegistrationRequiredMixin, View):
    def get(self, request):
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


class PayInvoicesSuccessView(RegistrationRequiredMixin, View):
    def get(self, request):
        session_id = request.GET.get('session_id', '')
        # If user refreshes it will not throw the ugly IntegrityError page
        try: 
            payment = Payment.objects.get(stripe_session_id=session_id)
        except ObjectDoesNotExist:
            total_amount = get_stripe_checkout_session_total(session_id)
            payment = Payment.objects.create(amount=total_amount, registration=self.registration, stripe_session_id=session_id)
        
        return redirect(reverse('invoices') + '?amount_paid=' + str(payment.amount))


class RegisterPolicyView(RegistrationRequiredMixin, UpdateView):
    template_name = 'registration/register_policy.html'
    form_class = RegisterPolicyForm
    success_url = reverse_lazy('register_forms')
    previous_url = 'index'

    def get_object(self):
        return self.registration


class RegisterFormsView(RegistrationRequiredMixin, TemplateView):
    template_name = 'registration/register_forms.html'

    def get(self, request):
        self.volunteer_form = RegVolunteerForm(instance=self.registration, prefix='volunteer_form')
        self.volunteer_details_form = RegVolunteerDetailsForm(instance=self.registration, prefix='volunteer_details_form')
        self.misc_form = RegMiscForm(instance=self.registration, prefix='misc_form')
        return super().get(request)

    def post(self, request):
        if 'next_button' in request.POST:
            self.volunteer_form = RegVolunteerForm(request.POST, instance=self.registration, prefix='volunteer_form')
            self.volunteer_details_form = RegVolunteerDetailsForm(instance=self.registration, prefix='volunteer_details_form')
            self.misc_form = RegMiscForm(request.POST, instance=self.registration, prefix='misc_form')
            if self.misc_form.is_valid() and self.volunteer_form.is_valid():
                if self.volunteer_form.cleaned_data['wants_to_volunteer']:
                    try:
                        volunteer = Volunteer.objects.get(registration=self.registration)
                    except ObjectDoesNotExist:
                        volunteer = Volunteer()
                        volunteer.save()
                        volunteer.registration = self.registration
                        volunteer.save()
                    self.volunteer_details_form = RegVolunteerDetailsForm(request.POST, request.FILES, instance=volunteer, prefix='volunteer_details_form')
                    if self.volunteer_details_form.is_valid():
                        self.volunteer_details_form.save()
                        self.misc_form.save()
                        self.volunteer_form.save()
                        return redirect('register_products')
                else:
                    try:
                        volunteer = Volunteer.objects.get(registration=self.registration)
                        volunteer.delete()
                    except ObjectDoesNotExist:
                        pass
                    self.misc_form.save()
                    self.volunteer_form.save()
                    return redirect('register_products')
            return super().get(request)
        else:
            return redirect('register_policy')


class RegisterAllProductsView(CreateOrderMixin, FormView):
    template_name = 'registration/register_products.html'
    form_class = RegCompCodeForm
    previous_button = SubmitButton('Previous')
    ap_yes_button = SubmitButton('claim_ap')
    ap_no_button = SubmitButton('not_ap')

    def get_success_url(self):
        if self.ap_yes_button.name in self.request.POST:
            if self.order.is_accessible_pricing or self.order.claim_accessible_pricing():
                return reverse('register_accessible_pricing')
            else:
                # TODO: Not sure what to do if this happens
                # self.ap_available = False
                # return super().get(self.request)
                return reverse('register_donate')

        elif self.ap_no_button.name in self.request.POST:
            self.order.revoke_accessible_pricing()
            return reverse('register_donate')

    def get_initial(self):
        return {
            'code': self.registration.comp_code.code if self.registration.comp_code else ''
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.ap_available = self.order.ap_eligible_amount <= self.order.get_available_ap_funds() or self.order.is_accessible_pricing

        context.update({
            'dance': get_context_for_product_selection(ProductCategory.DANCE, self.request.user),
            'class': get_context_for_product_selection(ProductCategory.CLASS, self.request.user),
            'showcase': get_context_for_product_selection(ProductCategory.SHOWCASE, self.request.user),
            'merch': get_context_for_product_selection(ProductCategory.MERCH, self.request.user)
        })

        return context

    def form_valid(self, form):
        with transaction.atomic():
            CompCode.objects.select_for_update()
            if form.cleaned_data.get('code'):
                self.registration.comp_code = CompCode.objects.get(code=form.cleaned_data.get('code'))
                self.registration.order_set.filter(session__isnull=False).delete()
                self.registration.save()
        return super().form_valid(form)


class AddItemView(OrderRequiredMixin, View):
    def post(self, request):
        return add_remove_item_view(request, self.order, self.order.add_item)


class RemoveItemView(OrderRequiredMixin, View):
    def post(self, request):
        return add_remove_item_view(request, self.order, self.order.remove_item)


class RegisterAccessiblePricingView(NonZeroOrderRequiredMixin, DispatchMixin, TemplateView):
    template_name = 'registration/register_accessible_pricing.html'
    previous_button = LinkButton('register_products', 'Previous')

    def dispatch_mixin(self, request):
        if not self.order.is_accessible_pricing:
            return redirect('register_products')

    def post(self, request):
        price = int(request.POST.get('price_submit', self.order.original_price))
        self.order.set_accessible_price(price)
        return redirect('make_payment')


class RegisterDonateView(NonZeroOrderRequiredMixin, DispatchMixin, UpdateView):
    template_name = 'registration/register_donate.html'
    form_class = RegisterDonateForm
    success_url = reverse_lazy('make_payment')
    previous_url = 'register_products'

    def get_object(self):
        # Used by UpdateView via the SingleObjectMixin to set the instance used by the ModelForm:
        return self.order

    def dispatch_mixin(self, request):
        if self.order.is_accessible_pricing:
            return redirect('register_products')
        self.existing_donation = self.order.donation
    
    def form_valid(self, form):
        if self.order.donation != self.existing_donation:
            self.order.invoice_set.all().delete()           
        return super().form_valid(form)


class MakePaymentView(NonZeroOrderRequiredMixin, TemplateView):
    template_name = 'registration/payment.html'
    previous_button = SubmitButton('Previous')
    back_to_selection = LinkButton('register_products', 'Back to Selection')

    def post(self, request):
        if self.previous_button.name in request.POST:
            if self.order.is_accessible_pricing:
                return redirect('register_products')
            else:
                return redirect('register_donate')

    def get(self, request):
        if self.order.accessible_price + self.order.donation == 0:
            return redirect('payment_confirmation')

        # Set default Payment Plan / resets on Refresh
        self.months_range = range(1, 5)
        self.payments_per_month = 1
        self.months = 1
        self.items = get_quantity_purchased_for_item(self.order.orderitem_set.order_by('product__category__section', 'product__category__rank', 'product__slots__rank'), request.user).iterator()
        self.items = map(add_quantity_range_to_item, self.items)

        return super().get(request)


class NewCheckoutView(NonZeroOrderRequiredMixin, View):
    def post(self, request):

        self.order.invoice_set.all().delete()
        payments_per_month = int(request.POST.get('ppm'))
        months = int(request.POST.get('months'))

        numOfPayments = payments_per_month * months
        individualPayment = int(self.order.total_price / numOfPayments)
        firstPayment = individualPayment + self.order.total_price - individualPayment * numOfPayments

        date = timezone.now()
        date_in_two_weeks = date + relativedelta(weeks=+2)

        first_invoice = Invoice.objects.create(order=self.order, pay_at_checkout=True, due_date=date, amount=firstPayment)
        if payments_per_month == 2:
            Invoice.objects.create(order=self.order, due_date=date_in_two_weeks, amount=individualPayment)

        for i in range(1, months):
            Invoice.objects.create(order=self.order, due_date=date+relativedelta(months=i), amount=individualPayment)
            if payments_per_month == 2:
                Invoice.objects.create(order=self.order, due_date=date_in_two_weeks+relativedelta(months=i), amount=individualPayment)

        # Stripe Session Code
        success_url = request.build_absolute_uri(reverse('payment_confirmation')) + '?session_id={CHECKOUT_SESSION_ID}'
        cancel_url = request.build_absolute_uri(reverse('make_payment'))

        try:
            checkout_session_id = create_stripe_checkout_session(firstPayment, success_url, cancel_url)
            
            # Provide public key to initialize Stripe Client in browser
            # And checkout session id
            return JsonResponse({
                'public_key': settings.STRIPE_PUBLIC_TEST_KEY,
                'session_id': checkout_session_id,
            })
        except Exception as e:
            return JsonResponse({'error': str(e)})


class PaymentConfirmationView(FinishedOrderRequiredMixin, TemplateView):
    template_name = 'registration/payment_confirmation.html'

    def get(self, request):
        request.session['payments_per_month'] = None
        request.session['months'] = None

        self.order.session = None
        self.order.save()
        create_or_update_subscriber(request.user, self.registration)

        send_confirmation(request.user, self.order)

        self.amount_due = self.order.invoice_set.get(pay_at_checkout=True).amount if self.order.invoice_set.exists() else 0
        self.items = self.order.orderitem_set.order_by('product__category__section', 'product__category__rank', 'product__slots__rank')
        self.invoices = self.order.invoice_set.filter(pay_at_checkout=False)

        return super().get(request)


