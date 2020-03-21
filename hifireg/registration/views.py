from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from .helpers.router import *


def index(request):
    maxindex = Registration.objects.count()-1
    form = tmpedit(maxindex=maxindex)
    print(form)
    return render(request, 'registration/index.html', {'maximum': maxindex, 'form': form})


def login(request):
    if request.method == 'POST':
        f = UserCreationForm(request.POST)
        if f.is_valid():
            f.save()
            messages.success(request, 'Account created successfully')
            return redirect('login')

    else:
        f = UserCreationForm()

    return render(request, 'registration/index.html', {'form': f})


def tmp_edit(request):
    if request.method == 'POST':
        form = tmpedit(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            dbindex = cd.get('index')
            reg = Registration.objects.all()[dbindex]
            f = policy_form(instance=reg)
            context = {'form': f, 'submit': 'submit'}
            return render(request, 'registration/reg_form.html', context)
        else:
            print('it broke')
            return redirect('login')


def form(request):
    f = policy_form()
    context = {'form': f}
    return render(request, 'registration/reg_form.html', context)


def registration_form_view(request):
    reg_inst_update = None

    if request.method == 'POST':
        # print('request.POST:')
        # print(request.POST)
        # see if there is saved data for this registration. If there is, get it. If not, record the
        try:
            instance = Registration.objects.get(id=request.session['reg_id'])
            f = mf_sel(request.POST, request.session['current_page'], instance)
        except KeyError:
            f = mf_sel(request.POST, request.session['current_page'])
            reg_inst_update = True
        # print('modelform populated with form data:')
        # print(f)
        if f.is_valid():
            # save form data
            reg_obj = f.save()  # result is registration object
            print('registration instance:')
            print(reg_obj)

            # oneshot: preserve registration id in session
            if reg_inst_update:
                request.session['reg_id'] = reg_obj.id

            print('registration id:')
            print(request.session['reg_inst'])

            # find navigation input in form data
            direction = None
            if 'next' in request.POST:
                direction = 'next'
            elif 'prev' in request.POST:
                direction = 'prev'
            elif 'submit' in request.POST:
                direction = 'submit'
            # elif direction is None:

            # if submitted, route to confirmation. Otherwise, route to next page.
            if 'submit' in direction:
                del request.session['reg_id']
                return redirect('confirmation')
            else:
                context = router(reg_obj, request.session['current_page'], direction)
                request.session['current_page'] = context['current_page']
                return render(request, 'registration/reg_form.html', context)
        else:
            print('it bork')
            print(f.errors)
            return redirect('index')
    else:
        context = router()
        request.session['current_page'] = context['current_page']
        return render(request, 'registration/reg_form.html', context)


def submit(request):
    print(request.POST)
    f = policy_form(request.POST)
    if f.is_valid():
        f.save()
        return redirect('confirmation')
    else:
        context = {'form': f}
        return render(request, 'registration/reg_form.html', context)


def confirmation(request):
    return render(request, 'registration/confirmation.html')
