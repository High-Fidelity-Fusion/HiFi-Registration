from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # path('', include('registration.urls')),
    path('registration/', include('registration.urls')),
    path('admin/', admin.site.urls),
]
