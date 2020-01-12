from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect


def index(request):
    return render(request, 'registration/index.html', {})

def login(request):
    if request.method == 'POST':
        f = UserCreationForm(request.POST)
        if f.is_valid():
            f.save()
            messages.success(request, 'Account created successfully')
            return redirect('login')

    else:
        f = UserCreationForm()

    return render(request, 'registration/login.html', {'form': f})

