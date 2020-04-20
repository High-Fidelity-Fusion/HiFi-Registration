from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from registration.forms import AuthenticationForm, UserCreationForm, UserUpdateForm
from registration.models import User

from .utils import SubmitButton, LinkButton


class LoginView(auth_views.LoginView):
    template_name = 'user/login.html'
    authentication_form = AuthenticationForm


class CreateUser(FormView):
    template_name = "user/create_user.html"
    form_class = UserCreationForm
    success_url = reverse_lazy('index')
    
    def form_valid(self, form):
        user = form.save()
        # https://docs.djangoproject.com/en/3.0/topics/auth/default/#how-to-log-a-user-in
        login(self.request, user)
        return super().form_valid(form)


@login_required
def view_user(request):
    context = {}
    context['title'] = "View Account"
    context['buttons'] = (LinkButton('Back', 'index'), 
                          LinkButton('Edit', 'edit_user'), 
                          LinkButton('Change Password', 'password_change'))
    context['form'] = UserUpdateForm(instance=request.user)
    for field in context['form'].fields.values():
        field.disabled = True
    return render(request, 'generic_form.html', context)


@login_required
def update_user(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('view_user')
    else:
        form = UserUpdateForm(instance=request.user)

    context = {}
    context['title'] = "Edit Account"
    context['buttons'] = (LinkButton('Cancel', 'view_user'), SubmitButton('Submit', 'submit'))
    context['form'] = form
    return render(request, 'generic_form.html', context)


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
