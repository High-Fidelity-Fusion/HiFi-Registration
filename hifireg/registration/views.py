from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView as LoginView_
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, DetailView

from .decorators import must_have_registration, must_have_order
from .forms import AuthenticationForm, UserCreationForm, UserUpdateForm, RegCompCodeForm, RegPolicyForm, RegVolunteerForm, RegVolunteerDetailsForm, RegMiscForm
from .models.registration import Registration, CompCode, Volunteer
from .models.user import User


@login_required
def index(request):
    return render(request, 'registration/index.html', {'user': request.user})


class LoginView(LoginView_):
    authentication_form = AuthenticationForm


def create_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully')
            login(request, user)
            # TODO: A lot of tutorials tend to authenticate the user before logging them in
            #       but I've seen this succeed without doing that. Probably need to figure
            #       out what the deal is there.
            return redirect('index')
    else:
        form = UserCreationForm()
    
    context = {'form': form}
    return render(request, 'registration/create_user.html', context)


@login_required
def view_user(request):
    if request.method == 'POST':
        if 'back' in request.POST:
            return redirect('index')
        else:
            return redirect('edit-user')

    instance = User.objects.get(email=request.user)
    form = UserUpdateForm(instance=instance)
    print(form.fields)
    for field in form.fields.values():
        print(field)
        field.disabled = True
    return render(request, 'registration/view_user.html', {'form': form})


@login_required
def update_user(request):
    user = User.objects.get(email=request.user)
    if request.method == 'POST':
        if 'cancel' in request.POST:
            return redirect('view-user')
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('view-user')
    else:
        form = UserUpdateForm(instance=user)
    return render(request, 'registration/edit_user.html', {'form': form})


@login_required
def register_comp_code(request):
    try:
        registration = Registration.objects.get(user=request.user)
    except ObjectDoesNotExist:
        registration = Registration(user=request.user)
        registration.save()

    next_page = 'register-policy'

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
            return redirect('register-comp-code')
        form = RegPolicyForm(request.POST, instance=Registration.objects.get(user=request.user))
        if form.is_valid():
            form.save()
            return redirect('register-ticket-selection')
    else:
        form = RegPolicyForm(instance=Registration.objects.get(user=request.user))
    return render(request, 'registration/register_policy.html', {'form': form})


@must_have_registration
def register_ticket_selection(request):
    form = None
    if request.method == 'POST':
        if 'previous' in request.POST:
            return redirect('register-policy')
        return redirect('register-class-selection')
    return render(request, 'registration/register_ticket_selection.html', {'form': form})


@must_have_registration  # change to must_have_order when orders are working
def register_class_selection(request):
    form = None
    if request.method == 'POST':
        if 'previous' in request.POST:
            return redirect('register-ticket-selection')
        return redirect('register-showcase')
    return render(request, 'registration/register_class_selection.html', {'form': form})


@must_have_registration  # change to must_have_order when orders are working
def register_showcase(request):
    form = None
    if request.method == 'POST':
        if 'previous' in request.POST:
            return redirect('register-class-selection')
        return redirect('register-merchandise')
    return render(request, 'registration/register_showcase.html', {'form': form})


@must_have_registration  # change to must_have_order when orders are working
def register_merchandise(request):
    form = None
    if request.method == 'POST':
        if 'previous' in request.POST:
            return redirect('register-showcase')
        return redirect('register-subtotal')
    return render(request, 'registration/register_merchandise.html', {'form': form})


# branch to accessible pricing or volunteering
@must_have_registration  # change to must_have_order when orders are working
def register_subtotal(request):
    form = None
    if request.method == 'POST':
        if 'previous' in request.POST:
            return redirect('register-showcase')
        if True: # redirect based on need for accessible pricing
            return redirect('register-accessible-pricing')
        else:
            return redirect('register-donate')
    return render(request, 'registration/register_subtotal.html', {'form': form})


@must_have_registration  # change to must_have_order when orders are working
def register_accessible_pricing(request):
    form = None
    if request.method == 'POST':
        if 'previous' in request.POST:
            return redirect('register-subtotal')
        return redirect('register-volunteer')
    return render(request, 'registration/register_accessible_pricing.html', {'form': form})


@must_have_registration  # change to must_have_order when orders are working
def register_donate(request):
    form = None
    if request.method == 'POST':
        if 'previous' in request.POST:
            return redirect('register-subtotal')
        return redirect('register-volunteer')
    return render(request, 'registration/register_donate.html', {'form': form})


@must_have_registration  # change to must_have_order when orders are working
def register_volunteer(request):
    if request.method == 'POST':
        if 'previous' in request.POST:
            if True:  # redirect based need for accessible pricing
                return redirect('register-donate')
            else:
                return redirect('register-accessible-pricing')
        form = RegVolunteerForm(request.POST, instance=Registration.objects.get(user=request.user))
        if form.is_valid():
            registration = form.save()
            if registration.wants_to_volunteer:
                return redirect('register-volunteer-details')
            else:
                return redirect('register-misc')
    else:
        form = RegVolunteerForm(instance=Registration.objects.get(user=request.user))
    return render(request, 'registration/register_volunteer.html', {'form': form})


@must_have_registration  # change to must_have_order when orders are working
def register_volunteer_details(request):
    registration = Registration.objects.get(user=request.user)
    try:
        volunteer = Volunteer.objects.all().get(id=registration.volunteer.id)
    except AttributeError:
        volunteer = Volunteer()
        volunteer.save()
        registration.volunteer = volunteer
        registration.save()

    if request.method == 'POST':
        if 'previous' in request.POST:
            return redirect('register-volunteer')
        form = RegVolunteerDetailsForm(request.POST, request.FILES, instance=volunteer)
        if form.is_valid():
            form.save()
            return redirect('register-misc')
    else:
        form = RegVolunteerDetailsForm(instance=volunteer)
    return render(request, 'registration/register_volunteer_details.html', {'form': form})


@must_have_registration  # change to must_have_order when orders are working
def register_misc(request):
    if request.method == 'POST':
        registration = Registration.objects.get(user=request.user)
        if 'previous' in request.POST:
            if registration.wants_to_volunteer:
                return redirect('register-volunteer-details')
            else:
                return redirect('register-volunteer')
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
            return redirect('register-misc')
        return redirect('payment-confirmation')
    else:
        return render(request, 'registration/payment.html', {'form': form})


def payment_confirmation(request):
    return render(request, 'registration/payment_confirmation.html', {})


# handles donations that are not part of registrations
def donate(request):
    return render(request, 'registration/donate.html', {})
