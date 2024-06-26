from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

import locator.views as views

urlpatterns = [
    path('get_country_code/', views.get_country_code, name='get_country_code'),
    path('get_country/', views.get_country, name='get_country'),
    path('get_city/', views.get_city, name='get_city'), ]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
