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


def index(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    context = {'user': request.user}
    return render(request, 'registration/index.html', context)


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


@method_decorator(login_required, name='dispatch')
class UpdateUser(UpdateView):
    model = User
    form_class = UserUpdateForm
    success_url = reverse_lazy('index')
    template_name = 'registration/edit_user.html'

    # prevents data from updating on post when cancel is pushed
    def post(self, request, *args, **kwargs):
        if 'cancel' in request.POST:
            self.object = self.get_object()
            return redirect('index')
        response = super(UpdateUser, self).post(request, *args, **kwargs)
        return response

    # modify get_object method to return object (avoids slug or pk in urlconf)
    def get_object(self):
        return User.objects.get(email=self.request.user)


@login_required
def view_user(request):
    instance = User.objects.get(email=request.user)
    form = UserUpdateForm(instance=instance)
    context = {'form': form}
    return render(request, 'registration/view_user.html', context)


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
    return render(request, 'registration/register_comp_code.html', {RegCompCodeForm.__name__: form})


class LoginView(LoginView_):
    authentication_form = AuthenticationForm


@must_have_registration
def register_policy(request):
    if request.method == 'POST':
        if 'previous' in request.POST:
            return redirect('register-comp-code')
        form = RegPolicyForm(request.POST, instance=Registration.objects.get(user=request.user))
        if form.is_valid():
            form.save()
            return redirect('register-volunteer')
    else:
        form = RegPolicyForm(instance=Registration.objects.get(user=request.user))
    return render(request, 'registration/register_policy.html', {'form': form})


@must_have_registration
def register_ticket_selection(request):
    form = None
    return render(request, 'registration/register_ticket_selection.html', {RegCompCodeForm.__name__: form})


@must_have_registration
def register_volunteer(request):
    if request.method == 'POST':
        if 'previous' in request.POST:
            return redirect('register-policy')
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


@must_have_registration
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


@must_have_registration
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
            return redirect('index')
    else:
        form = RegMiscForm(instance=Registration.objects.get(user=request.user))
    return render(request, 'registration/register_misc.html', {'form': form})