from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import FormView, UpdateView

from registration.forms import AuthenticationForm, UserCreationForm, UserUpdateForm, PasswordChangeForm, SetPasswordForm
from registration.models import User

from .mixins import FunctionBasedView
from .utils import SubmitButton, LinkButton


class LoginView(auth_views.LoginView):
    template_name = 'user/login.html'
    authentication_form = AuthenticationForm


class CreateUserView(FormView):
    template_name = "utils/generic_form.html"
    form_class = UserCreationForm
    success_url = reverse_lazy('index')
    extra_context = dict(title="Create Account", buttons=[SubmitButton("submit", "Submit")])

    def form_valid(self, form):
        user = form.save()
        # https://docs.djangoproject.com/en/3.0/topics/auth/default/#how-to-log-a-user-in
        login(self.request, user)
        return super().form_valid(form)


class ViewUserView(LoginRequiredMixin, View):
    def get(self, request):
        context = {}
        context['title'] = "View Account"
        context['buttons'] = [LinkButton("index", "Back"), 
                            LinkButton("edit_user", "Edit"), 
                            LinkButton("password_change", "Change Password")]
        context['form'] = UserUpdateForm(instance=request.user)
        for field in context['form'].fields.values():
            field.disabled = True
        return render(request, 'utils/generic_form.html', context)


class UpdateUserView(LoginRequiredMixin, UpdateView):
    template_name = 'utils/generic_form.html'
    form_class = UserUpdateForm
    success_url = reverse_lazy('view_user')
    extra_context = dict(title="Edit Account", 
                         buttons=[LinkButton("view_user", "Cancel"), SubmitButton("submit", "Submit")])
    
    def get_object(self):
        return self.request.user


class PasswordChangeView(auth_views.PasswordChangeView):
    form_class = PasswordChangeForm
    template_name = 'utils/generic_form.html'
    success_url = reverse_lazy('password_change_done')
    extra_context = dict(buttons=[LinkButton("view_user", "Cancel"), SubmitButton("submit", "Submit")])


class PasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    template_name = 'utils/generic_form.html'
    extra_context = dict(buttons=[LinkButton("view_user", "Account"), LinkButton("index", "Home")])


# allows user to generate reset password link
class PasswordResetView(auth_views.PasswordResetView):
    template_name = 'utils/generic_form.html'
    success_url = reverse_lazy('password_reset_done')
    extra_context = dict(buttons=[LinkButton("login", "Cancel"), SubmitButton("submit", "Submit")])


# confirms reset password link sent
class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'user/password_reset_done.html'


# accepts user's new password input
class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    form_class = SetPasswordForm
    template_name = 'utils/generic_form.html'
    success_url = reverse_lazy('password_reset_complete')
    extra_context = dict(buttons=[SubmitButton("submit", "Submit")])


# confirms user's new password input
class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'utils/generic_form.html'
    extra_context = dict(buttons=[LinkButton("login", "Login")])
