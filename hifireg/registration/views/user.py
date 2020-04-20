from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from registration.forms import AuthenticationForm, UserCreationForm, UserUpdateForm, PasswordChangeForm, SetPasswordForm
from registration.models import User

from .utils import SubmitButton, LinkButton


class LoginView(auth_views.LoginView):
    template_name = 'user/login.html'
    authentication_form = AuthenticationForm


class CreateUser(FormView):
    template_name = "generic_form.html"
    form_class = UserCreationForm
    success_url = reverse_lazy('index')
    extra_context = {'title': 'Create Account', 'buttons': (SubmitButton('Submit'),)}
    
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
    context['buttons'] = (LinkButton('Cancel', 'view_user'), SubmitButton('Submit'))
    context['form'] = form
    return render(request, 'generic_form.html', context)


class PasswordChangeView(auth_views.PasswordChangeView):
    form_class = PasswordChangeForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('password_change_done')
    extra_context = {}
    extra_context['buttons'] = (LinkButton('Cancel', 'view_user'), SubmitButton('Submit'))


class PasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    template_name = 'generic_form.html'
    extra_context = {}
    extra_context['buttons'] = (LinkButton('Account', 'view_user'), LinkButton('Home', 'index'))


# allows user to generate reset password link
class PasswordResetView(auth_views.PasswordResetView):
    template_name = 'generic_form.html'
    success_url = reverse_lazy('password_reset_done')
    extra_context = {}
    extra_context['buttons'] = (LinkButton('Cancel', 'login'), SubmitButton('Submit'))


# confirms reset password link sent
class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'user/password_reset_done.html'


# accepts user's new password input
class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    form_class = SetPasswordForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('password_reset_complete')
    extra_context = {'buttons': (SubmitButton('Submit'),)}


# confirms user's new password input
class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'generic_form.html'
    extra_context = {'buttons': (LinkButton('Login', 'login'),)}

