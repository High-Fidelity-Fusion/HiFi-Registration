from django.contrib.auth import views as auth_views
from django.urls import include, path

from . import views

# app_name = "registration" # a namespace for the named URLs

urlpatterns = [
    path('', views.index, name='index'),
    path('make-account/', views.create_user, name='create-user'),
    path('comp/', views.register_comp_code, name='register-comp-code'),
    path('ticket/', views.register_ticket_selection, name='register-ticket-selection'),
    path('form/', views.form, name='form'),
    path('submit/', views.submit, name='submit'),

    # TODO: implement templates for more of these
    # auth views (some are overridden in views)
    path('account/login/', views.LoginView.as_view(), name='login'),
    path('account/logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('account/password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('account/password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    path('account/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('account/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('account/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('account/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]