from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .forms import UserCreationForm
from .forms import RegistrationForm


def index(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    context = { 'user': request.user }
    return render(request, 'registration/index.html', context)


def create_user(request):
    if request.method == 'POST':
        f = UserCreationForm(request.POST)
        if f.is_valid():
            user = f.save()
            messages.success(request, 'Account created successfully')
            login(request, user)
            # TODO: A lot of tutorials tend to authenticate the user before logging them in
            #       but I've seen this succeed without doing that. Probably need to figure
            #       out what the deal is there.
            return redirect('index')
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
        return redirect('index')
    else:
        context = {'error_message': "Sucks to suck."}
        return render(request, 'registration/form.html', context)