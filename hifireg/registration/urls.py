from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('registration_form', views.registration_form_view, name='registration_form'),
    # path('tmp_edit', views.tmp_edit, name="tmp_edit"),
    path('confirmation', views.confirmation, name="confirmation"),
]