from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError
from django.shortcuts import render, redirect

from registration.forms import RegCompCodeForm, RegPolicyForm, RegVolunteerForm, RegVolunteerDetailsForm, RegMiscForm
from registration.models import CompCode, Order, ProductCategory, Registration, Volunteer

from .helpers import get_context_for_product_selection
from .decorators import must_have_registration, must_have_order


@login_required
def index(request):
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


@must_have_registration
def register_ticket_selection(request):
    if request.method == 'POST':
        if 'previous' in request.POST:
            return redirect('register_policy')
        return redirect('register_class_selection')

    order, created = Order.objects.update_or_create(registration=request.user.registration_set.get(), session__isnull=False, defaults={'session': Session.objects.get(pk=request.session.session_key)})

    context = get_context_for_product_selection(ProductCategory.DANCE, request.user)

    return render(request, 'registration/register_ticket_selection.html', context)


@must_have_registration  # change to must_have_order when orders are working
def register_class_selection(request):
    form = None
    if request.method == 'POST':
        if 'previous' in request.POST:
            return redirect('register_ticket_selection')
        return redirect('register_showcase')
    return render(request, 'registration/register_class_selection.html', {'form': form})


@must_have_registration  # change to must_have_order when orders are working
def register_showcase(request):
    form = None
    if request.method == 'POST':
        if 'previous' in request.POST:
            return redirect('register_class_selection')
        return redirect('register_merchandise')
    return render(request, 'registration/register_showcase.html', {'form': form})


@must_have_registration  # change to must_have_order when orders are working
def register_merchandise(request):
    form = None
    if request.method == 'POST':
        if 'previous' in request.POST:
            return redirect('register_showcase')
        return redirect('register_subtotal')
    return render(request, 'registration/register_merchandise.html', {'form': form})


# branch to accessible pricing or volunteering
@must_have_registration  # change to must_have_order when orders are working
def register_subtotal(request):
    form = None
    if request.method == 'POST':
        if 'previous' in request.POST:
            return redirect('register_merchandise')
        if True: # redirect based on need for accessible pricing
            return redirect('register_accessible_pricing')
        else:
            return redirect('register_donate')
    return render(request, 'registration/register_subtotal.html', {'form': form})


@must_have_registration  # change to must_have_order when orders are working
def register_accessible_pricing(request):
    form = None
    if request.method == 'POST':
        if 'previous' in request.POST:
            return redirect('register_subtotal')
        return redirect('register_volunteer')
    return render(request, 'registration/register_accessible_pricing.html', {'form': form})


@must_have_registration  # change to must_have_order when orders are working
def register_donate(request):
    form = None
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
