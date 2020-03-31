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
    path('account/', include('django.contrib.auth.urls')),
]