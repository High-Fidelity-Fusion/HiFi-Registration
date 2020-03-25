from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('make-account/', views.create_user, name='create-user'),
    path('form/', views.form, name='form'),
    path('submit/', views.submit, name='submit'),
    path('account/', include('django.contrib.auth.urls')),
]