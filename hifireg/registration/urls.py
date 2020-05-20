from django.contrib.auth import views as auth_views
from django.urls import include, path, reverse_lazy
from django.views.generic.base import RedirectView

from . import views


# app_name = "registration" # a namespace for the named URLs

urlpatterns = [
    # index:
    path('', views.Index.as_view(), name='index'),

    # must have registration:
    path('register/', RedirectView.as_view(url=reverse_lazy('register_comp_code')), name='registration'), # redirects to registration creation view
    path('register/comp/', views.register_comp_code, name='register_comp_code'),
    path('register/policy/', views.register_policy, name='register_policy'),

    # must have order:
    path('register/order/', RedirectView.as_view(url=reverse_lazy('register_ticket_selection')), name='order'), # redirects to order creation view
    path('ajax/add_item/', views.add_item, name='add_item'),
    path('ajax/remove_item/', views.remove_item, name='remove_item'),
    path('register/ticket/', views.register_ticket_selection, name='register_ticket_selection'),
    path('register/classes/', views.register_class_selection, name='register_class_selection'),
    path('register/showcase/', views.register_showcase, name='register_showcase'),
    path('register/merchandise/', views.register_merchandise, name='register_merchandise'),

    path('register/subtotal/', views.RegisterSubtotal.as_view(), name='register_subtotal'),
    path('register/accessible-pricing/', views.RegisterAP.as_view(), name='register_accessible_pricing'),
    path('register/donate/', views.register_donate, name='register_donate'),
    path('register/volunteer/', views.register_volunteer, name='register_volunteer'),
    path('register/volunteer/details/', views.register_volunteer_details, name='register_volunteer_details'),
    path('register/miscellaneous/', views.register_misc, name='register_misc'),

    # payment:
    path('payment/', views.registration.make_payment, name='payment'),
    path('payment/confirmation/', views.registration.payment_confirmation, name='payment_confirmation'),

    # auth/account views (some are overridden in views)
    path('account/create/', views.CreateUser.as_view(), name='create_user'),
    path('account/view/', views.view_user, name='view_user'),
    path('account/edit/', views.update_user, name='edit_user'),
    path('account/login/', views.LoginView.as_view(), name='login'),
    path('account/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('account/password-change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('account/password-change/done/', views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('account/password-reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('account/password-reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('account/reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('account/reset/done/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
