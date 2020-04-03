from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView as LoginView_
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView

from .decorators import must_have_registration, must_have_order
from .forms import AuthenticationForm, UserCreationForm, RegCompCodeForm, UserUpdateForm
from .models.registration import Registration, CompCode
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


@login_required
class UpdateUser(UpdateView):
    model = User
    form_class = UserUpdateForm
    success_url = reverse_lazy('index')
    template_name = 'registration/edit_user.html'

    # prevents data from updating on post when cancel is pushed
    def post(self, request, *args, **kwargs):
        print(request.POST)
        if 'cancel' in request.POST:
            self.object = self.get_object()
            return redirect('index')
        response = super(UpdateUser, self).post(request, *args, **kwargs)
        return response

    # modify get_object method to return object (avoids slug or pk in urlconf)
    def get_object(self):
        return User.objects.get(email=self.request.user)

    # use default view, but decorate it
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        response = super(UpdateUser, self).dispatch(request, *args, **kwargs)
        return response


@login_required
def register_comp_code(request):
    try:
        registration = Registration.objects.get(user=request.user)
    except ObjectDoesNotExist:
        registration = Registration(user=request.user)
        registration.save()

    nextPage = 'index'

    # Skip condition
    if registration.comp_code is not None:
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


class LoginView(LoginView_):
    authentication_form = AuthenticationForm
