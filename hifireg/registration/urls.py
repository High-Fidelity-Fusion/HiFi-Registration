from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('form', views.form, name='form'),
    path('registration_form', views.registration_form_view, name='registration_form'),
    path('submit', views.submit, name='submit'),
    path('tmp_edit', views.tmp_edit, name="tmp_edit"),
    path('confirmation', views.confirmation, name="confirmation"),
]