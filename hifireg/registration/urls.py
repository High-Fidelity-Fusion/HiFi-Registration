from django.contrib.auth import views as auth_views
from django.urls import include, path, reverse_lazy
from django.views.generic.base import RedirectView

from .views import registration, user


# app_name = "registration" # a namespace for the named URLs

urlpatterns = [
    # index:
    path('', registration.index, name='index'),

    # must have registration:
    path('register/', RedirectView.as_view(url=reverse_lazy('register_comp_code')), name='registration'), # redirects to registration creation view
    path('register/comp/', registration.register_comp_code, name='register_comp_code'),
    path('register/policy/', registration.register_policy, name='register_policy'),

    # must have order:
    path('register/order', RedirectView.as_view(url=reverse_lazy('register_ticket_selection')), name='order'), # redirects to order creation view
    path('register/ticket/', registration.register_ticket_selection, name='register_ticket_selection'),
    path('register/classes/', registration.register_class_selection, name='register_class_selection'),
    path('register/showcase/', registration.register_showcase, name='register_showcase'),
    path('register/merchandise/', registration.register_merchandise, name='register_merchandise'),

    path('register/subtotal/', registration.register_subtotal, name='register_subtotal'),
    path('register/accessible-pricing/', registration.register_accessible_pricing, name='register_accessible_pricing'),
    path('register/donate/', registration.register_donate, name='register_donate'),
    path('register/volunteer/', registration.register_volunteer, name='register_volunteer'),
    path('register/volunteer/details/', registration.register_volunteer_details, name='register_volunteer_details'),
    path('register/miscellaneous/', registration.register_misc, name='register_misc'),

    # payment:
    path('payment/', registration.make_payment, name='payment'),
    path('payment/confirmation/', registration.payment_confirmation, name='payment_confirmation'),

    # auth/account views (some are overridden in views)
    path('account/create/', user.CreateUser.as_view(), name='create_user'),
    path('account/view/', user.view_user, name='view_user'),
    path('account/edit/', user.update_user, name='edit_user'),
    path('account/login/', user.LoginView.as_view(), name='login'),
    path('account/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('account/password-change/', user.PasswordChangeView.as_view(), name='password_change'),
    path('account/password-change/done/', user.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('account/password-reset/', user.PasswordResetView.as_view(), name='password_reset'),
    path('account/password-reset/done/', user.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('account/reset/<uidb64>/<token>/', user.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('account/reset/done/', user.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
