from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView as LoginView_
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError
from django.shortcuts import render, redirect

from .decorators import must_have_registration, must_have_order
from .forms import AuthenticationForm
from .forms import UserCreationForm
from .forms import RegistrationForm
from .forms import RegCompCodeForm
from .models.registration import Registration, CompCode


def index(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    context = { 'user': request.user }
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


@login_required
def register_comp_code(request):
    try:
        registration = Registration.objects.get(user=request.user)
    except ObjectDoesNotExist:
        registration = Registration(user=request.user)
        registration.save()

    nextPage = 'index'

    # Skip condition
    if (registration.comp_code is not None):
        return redirect(nextPage)

    if request.method == 'POST':
        form = RegCompCodeForm(request.POST)

        with transaction.atomic():
            CompCode.objects.select_for_update()
            if form.is_valid():
                if form.cleaned_data.get('code'):
                    registration.comp_code = CompCode.objects.get(code=form.cleaned_data.get('code'))
                    registration.order_set.filter(session__isnull=False).delete()
                    registration.save()
                return redirect(nextPage)

    else:
        form = RegCompCodeForm(initial={'code': registration.comp_code.code if registration.comp_code else ''})
    return render(request, 'registration/register_comp_code.html', {RegCompCodeForm.__name__: form})

@login_required
@must_have_registration
def register_ticket_selection(request):
    return render(request, 'registration/register_ticket_selection.html', {RegCompCodeForm.__name__: form})


def form(request):
    f = RegistrationForm()
    context = {'registration_form' : f}
    return render(request,'registration/form_test.html', context)


def submit(request):
    f = RegistrationForm(request.POST or None)
    if f.is_valid():
        f.save()
        return redirect('index')
    else:
        context = {'error_message': "Sucks to suck."}
        return render(request, 'registration/form_test.html', context)


class LoginView(LoginView_):
    authentication_form = AuthenticationForm
