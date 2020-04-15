from django.contrib.auth import views as auth_views
from django.urls import include, path, reverse_lazy

from . import views


# app_name = "registration" # a namespace for the named URLs

urlpatterns = [
    path('', views.index, name='index'),
    path('form/comp/', views.register_comp_code, name='register_comp_code'),
    path('form/policy/', views.register_policy, name='register_policy'),
    path('form/ticket/', views.register_ticket_selection, name='register_ticket_selection'),
    path('form/classes/', views.register_class_selection, name='register_class_selection'),
    path('form/showcase/', views.register_showcase, name='register_showcase'),
    path('form/merchandise/', views.register_merchandise, name='register_merchandise'),
    path('form/subtotal/', views.register_subtotal, name='register_subtotal'),
    path('form/accessible-pricing/', views.register_accessible_pricing, name='register_accessible_pricing'),
    path('form/donate/', views.register_donate, name='register_donate'),
    path('form/volunteer/', views.register_volunteer, name='register_volunteer'),
    path('form/volunteer/details/', views.register_volunteer_details, name='register_volunteer_details'),
    path('form/miscellaneous/', views.register_misc, name='register_misc'),
    path('payment/', views.make_payment, name='payment'),
    path('payment/confirmation/', views.payment_confirmation, name='payment_confirmation'),


    # auth views (some are overridden in views)
    path('account/create', views.create_user, name='create_user'),
    path('account/view', views.view_user, name='view_user'),
    path('account/edit', views.update_user, name='edit_user'),
    path('account/login/', views.LoginView.as_view(), name='login'),
    path('account/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('account/password-change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('account/password-change/done/', views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('account/password-reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('account/password-reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('account/reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('account/reset/done/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
