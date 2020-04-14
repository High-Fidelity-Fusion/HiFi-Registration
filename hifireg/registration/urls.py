from django.contrib.auth import views as auth_views
from django.urls import include, path

from . import views

# app_name = "registration" # a namespace for the named URLs

urlpatterns = [
    path('', views.index, name='index'),
    path('form/comp/', views.register_comp_code, name='register-comp-code'),
    path('form/policy/', views.register_policy, name='register-policy'),
    path('form/ticket/', views.register_ticket_selection, name='register-ticket-selection'),
    path('form/classes/', views.register_class_selection, name='register-class-selection'),
    path('form/showcase/', views.register_showcase, name='register-showcase'),
    path('form/merchandise/', views.register_merchandise, name='register-merchandise'),
    path('form/subtotal/', views.register_subtotal, name='register-subtotal'),
    path('form/accessible-pricing/', views.register_accessible_pricing, name='register-accessible-pricing'),
    path('form/donate/', views.register_donate, name='register-donate'),
    path('form/volunteer/', views.register_volunteer, name='register-volunteer'),
    path('form/volunteer/details/', views.register_volunteer_details, name='register-volunteer-details'),
    path('form/miscellaneous/', views.register_misc, name='register-misc'),
    path('payment/', views.make_payment, name='payment'),
    path('payment/confirmation/', views.payment_confirmation, name='payment-confirmation'),

    path('account/create', views.create_user, name='create-user'),
    path('account/view', views.view_user, name='view-user'),
    path('account/edit', views.update_user, name='edit-user'),

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