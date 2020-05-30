from django.contrib.auth import views as auth_views
from django.urls import include, path, reverse_lazy
from django.views.generic.base import RedirectView

from . import views


# app_name = "registration" # a namespace for the named URLs

urlpatterns = [
    # index:
    path('', views.IndexView.as_view(), name='index'),

    # must have registration:
    path('register/', RedirectView.as_view(url=reverse_lazy('register_comp_code')), name='registration'), # redirects to registration creation view
    path('register/comp/', views.RegisterCompCodeView.as_view(), name='register_comp_code'),
    path('register/policy/', views.RegisterPolicyView.as_view(), name='register_policy'),

    # must have order:
    path('register/order/', RedirectView.as_view(url=reverse_lazy('register_ticket_selection')), name='order'), # redirects to order creation view
    path('ajax/add_item/', views.AddItemView.as_view(), name='add_item'),
    path('ajax/remove_item/', views.RemoveItemView.as_view(), name='remove_item'),
    path('register/ticket/', views.RegisterTicketSelectionView.as_view(), name='register_ticket_selection'),
    path('register/classes/', views.RegisterClassSelectionView.as_view(), name='register_class_selection'),
    path('register/showcase/', views.RegisterShowcaseView.as_view(), name='register_showcase'),
    path('register/merchandise/', views.RegisterMerchandiseView.as_view(), name='register_merchandise'),

    path('register/subtotal/', views.RegisterSubtotal.as_view(), name='register_subtotal'),
    path('register/accessible-pricing/', views.RegisterAccessiblePricingView.as_view(), name='register_accessible_pricing'),
    path('register/donate/', views.RegisterDonateView.as_view(), name='register_donate'),
    path('register/volunteer/', views.RegisterVolunteerView.as_view(), name='register_volunteer'),
    path('register/volunteer/details/', views.RegisterVolunteerDetailsView.as_view(), name='register_volunteer_details'),
    path('register/miscellaneous/', views.RegisterMiscView.as_view(), name='register_misc'),

    # payment:
    path('payment/', views.MakePaymentView.as_view(), name='make_payment'),
    path('payment/confirmation/', views.PaymentConfirmationView.as_view(), name='payment_confirmation'),

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
