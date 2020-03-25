from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect
from .forms import UserCreationForm
from .forms import RegistrationForm


def index(request):
    # if not logged in -- redirect to make-account
    if not request.user.is_authenticated:
        return redirect('create-user')

    return render(request, 'registration/index.html')

def create_user(request):
    if request.method == 'POST':
        f = UserCreationForm(request.POST)
        if f.is_valid():
            f.save()
            messages.success(request, 'Account created successfully')
            return redirect('login')

    else:
        f = UserCreationForm()

    return render(request, 'registration/create_user.html', {'form': f})

def form(request):
    f = RegistrationForm()
    context = {'registration_form' : f}
    return render(request,'registration/form.html', context)

def submit(request):
    f = RegistrationForm(request.POST or None)
    if f.is_valid():
        f.save()
        return render(request,'registration/index.html')
    else:
        return render(request, 'registration/form.html'),{'error_message': "Sucks to suck."}