from django.contrib.auth import views as auth_views
from django.urls import include, path, reverse_lazy
from django.views.generic.base import RedirectView

from . import views


# app_name = "registration" # a namespace for the named URLs

urlpatterns = [
    # index:
    path('', views.IndexView.as_view(), name='index'),
    path('orders', views.OrdersView.as_view(), name='orders'),

    #testing email:
    path('order/send-email', views.SendEmail.as_view(), name='send_email'),

    # beta login url:
    path('beta-login/', views.BetaLoginView.as_view(), name='beta_login'),

    # must have registration:
    path('register/policy/', views.RegisterPolicyView.as_view(), name='register_policy'),
    path('register/forms/', views.RegisterFormsView.as_view(), name='register_forms'),

    # must have order:
    path('register/selection/', views.RegisterAllProductsView.as_view(), name='register_products'),
    path('ajax/add_item/', views.AddItemView.as_view(), name='add_item'),
    path('ajax/remove_item/', views.RemoveItemView.as_view(), name='remove_item'),
    path('register/accessible-pricing/', views.RegisterAccessiblePricingView.as_view(), name='register_accessible_pricing'),
    path('register/donate/', views.RegisterDonateView.as_view(), name='register_donate'),

    # payment:
    path('payment/', views.MakePaymentView.as_view(), name='make_payment'),
    path('payment/new-checkout/', views.NewCheckoutView.as_view(), name='new_checkout'),
    path('payment/confirmation/', views.PaymentConfirmationView.as_view(), name='payment_confirmation'),

    # post-order invoices to be paid
    path('invoices/', views.InvoicesView.as_view(), name='invoices'),
    path('invoices/pay/', views.PayInvoicesView.as_view(), name='pay_invoices'),
    path('invoices/pay/success/', views.PayInvoicesSuccessView.as_view(), name='pay_success'),

    # auth/account views (some are overridden in views)
    path('account/create/', views.CreateUserView.as_view(), name='create_user'),
    path('account/view/', views.ViewUserView.as_view(), name='view_user'),
    path('account/edit/', views.UpdateUserView.as_view(), name='edit_user'),
    path('account/login/', views.LoginView.as_view(), name='login'),
    path('account/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('account/password-change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('account/password-change/done/', views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('account/password-reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('account/password-reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('account/reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('account/reset/done/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
