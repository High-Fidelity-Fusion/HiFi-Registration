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

import stripe

from registration.forms import RegCompCodeForm, RegPolicyForm, RegDonateForm, RegVolunteerForm, RegVolunteerDetailsForm, RegMiscForm
from registration.models import CompCode, Order, ProductCategory, Registration, Volunteer, Product, APFund

from .mixins import RegistrationRequiredMixin, OrderRequiredMixin, NonZeroOrderRequiredMixin, PolicyRequiredMixin
from .mixins import DispatchMixin, FunctionBasedView
from .utils import SubmitButton, LinkButton
from .helpers import get_context_for_product_selection


class IndexView(LoginRequiredMixin, TemplateView):
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


class RegisterTicketSelectionView(PolicyRequiredMixin, FunctionBasedView, View):
    def fbv(self, request):
        if request.method == 'POST':
            if 'previous' in request.POST:
                return redirect('register_policy')
            return redirect('register_class_selection')

        order, created = Order.objects.update_or_create(
            registration=request.user.registration_set.get(), 
            session__isnull=False, 
            defaults={'session': Session.objects.get(pk=request.session.session_key)})

        context = get_context_for_product_selection(ProductCategory.DANCE, request.user)

        return render(request, 'registration/register_selection.html', context)


class RegisterClassSelectionView(OrderRequiredMixin, FunctionBasedView, View):
    def fbv(self, request):
        if request.method == 'POST':
            if 'previous' in request.POST:
                return redirect('register_ticket_selection')
            return redirect('register_showcase')

        context = get_context_for_product_selection(ProductCategory.CLASS, request.user)

        return render(request, 'registration/register_selection.html', context)


class RegisterShowcaseView(OrderRequiredMixin, FunctionBasedView, View):
    def fbv(self, request):
        if request.method == 'POST':
            if 'previous' in request.POST:
                return redirect('register_class_selection')
            return redirect('register_merchandise')

        order, created = Order.objects.update_or_create(
            registration=request.user.registration_set.get(), 
            session__isnull=False, 
            defaults={'session': Session.objects.get(pk=request.session.session_key)})

        context = get_context_for_product_selection(ProductCategory.SHOWCASE, request.user)

        return render(request, 'registration/register_selection.html', context)


class RegisterMerchandiseView(OrderRequiredMixin, FunctionBasedView, View):
    def fbv(self, request):
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


class RegisterDonateView(OrderRequiredMixin, FunctionBasedView, View):
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


class RegisterVolunteerView(PolicyRequiredMixin, FunctionBasedView, View):
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


class RegisterVolunteerDetailsView(PolicyRequiredMixin, FunctionBasedView, View):
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


class RegisterMiscView(PolicyRequiredMixin, FunctionBasedView, View):
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


class PaymentPlan(View):
    def get(self, request):
        return render(request, 'registration/payment_plan.html', {})



class MakePaymentView(PolicyRequiredMixin, FunctionBasedView, View):
    def fbv(self, request):
        form = None
        if request.method == 'POST':
            if 'previous' in request.POST:
                return redirect('payment_plan')
            return redirect('payment_confirmation')
        else:
            return render(request, 'registration/payment.html', {'form': form})


class NewCheckoutView(PolicyRequiredMixin, FunctionBasedView, View):
    def fbv(self, request):
        if request.method == 'GET':
            # configure Stripe w/secret API key
            stripe.api_key = settings.STRIPE_SECRET_TEST_KEY

            # Using fake amount and variable because real variable unknown atm 6.15.20
            reg_amount = 150000

            # urls for recieving redirects from Stripe
            success_url = request.build_absolute_uri(reverse('payment_confirmation') + '?session_id={CHECKOUT_SESSION_ID}')
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


class PaymentConfirmationView(FunctionBasedView, View):
    def fbv(self, request):
        return render(request, 'registration/payment_confirmation.html', {})
