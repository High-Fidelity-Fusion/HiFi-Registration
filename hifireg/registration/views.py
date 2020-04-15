from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator

from .decorators import must_have_registration, must_have_order
from .forms import AuthenticationForm, UserCreationForm, UserUpdateForm, RegCompCodeForm, RegPolicyForm, RegVolunteerForm, RegVolunteerDetailsForm, RegMiscForm
from .models.registration import Registration, CompCode, Volunteer
from .models.user import User


@login_required
def index(request):
    return render(request, 'registration/index.html', {'user': request.user})


class LoginView(auth_views.LoginView):
    template_name = 'user/login.html'
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
    return render(request, 'user/create_user.html', context)


@login_required
def view_user(request):
    instance = User.objects.get(email=request.user)
    form = UserUpdateForm(instance=instance)
    for field in form.fields.values():
        field.disabled = True
    return render(request, 'user/view_user.html', {'form': form})


@login_required
def update_user(request):
    user = User.objects.get(email=request.user)
    if request.method == 'POST':
        if 'cancel' in request.POST:
            return redirect('view_user')
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('view_user')
    else:
        form = UserUpdateForm(instance=user)
    return render(request, 'user/edit_user.html', {'form': form})


class PasswordChangeView(auth_views.PasswordChangeView):
    template_name = 'user/password_change.html'
    success_url = reverse_lazy('password_change_done')

    def post(self, request, *args, **kwargs):
        if 'cancel' in request.POST:
            return redirect('view_user')
        return super(PasswordChangeView, self).post(request, *args, **kwargs)


class PasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    template_name = 'user/password_change_done.html'


# allows user to generate reset password link
class PasswordResetView(auth_views.PasswordResetView):
    template_name = 'user/password_reset.html'
    success_url = reverse_lazy('password_reset_done')

    def post(self, request, *args, **kwargs):
        if 'cancel' in request.POST:
            return redirect('login')
        return super(PasswordResetView, self).post(request, *args, **kwargs)


# confirms reset password link sent
class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'user/password_reset_done.html'


# accepts user's new password input
class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'user/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


# confirms user's new password input
class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'user/password_reset_complete.html'


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
    form = None
    if request.method == 'POST':
        if 'previous' in request.POST:
            return redirect('register_policy')
        return redirect('register_class_selection')
    return render(request, 'registration/register_ticket_selection.html', {'form': form})


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
        volunteer = Volunteer.objects.all().get(id=registration.volunteer.id)
    except AttributeError:
        volunteer = Volunteer()
        volunteer.save()
        registration.volunteer = volunteer
        registration.save()

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
