from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from ..forms.user import AuthenticationForm, UserCreationForm, UserUpdateForm
from ..models.user import User


class LoginView(auth_views.LoginView):
    template_name = 'user/login.html'
    authentication_form = AuthenticationForm


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
    return render(request, 'user/create_user.html', context)


@login_required
def view_user(request):
    instance = User.objects.get(email=request.user)
    form = UserUpdateForm(instance=instance)
    for field in form.fields.values():
        field.disabled = True
    return render(request, 'user/view_user.html', {'form': form})


@login_required
def update_user(request):
    user = User.objects.get(email=request.user)
    if request.method == 'POST':
        if 'cancel' in request.POST:
            return redirect('view_user')
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('view_user')
    else:
        form = UserUpdateForm(instance=user)
    return render(request, 'user/edit_user.html', {'form': form})


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
