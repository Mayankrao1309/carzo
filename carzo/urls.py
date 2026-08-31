"""
URL configuration for carzo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.shortcuts import redirect

from app import admin_views

useradmin_patterns = ([
    path('', admin_views.admin_panel, name='admin-panel'),
    path('admins/add/', admin_views.admin_add, name='admin-add'),
    path('admins/delete/<int:uid>/', admin_views.admin_delete, name='admin-delete'),
    path('admins/edit/<int:uid>/', admin_views.admin_edit, name='admin-edit'),
    path('owners/save/', admin_views.owner_save, name='owner-save'),
    path('owners/delete/<int:oid>/', admin_views.owner_delete, name='owner-delete'),
    path('cars/save/', admin_views.car_save, name='car-save'),
    path('cars/delete/<str:cid>/', admin_views.car_delete, name='car-delete'),
    path('cars/toggle-availability/<str:cid>/', admin_views.car_toggle_availability, name='car-toggle-availability'),
    path('bookings/<str:bid>/json/', admin_views.booking_detail_json, name='booking-detail-json'),
    path('bookings/toggle-delivery/<str:bid>/', admin_views.booking_toggle_delivery, name='booking-toggle-delivery'),
    path('categories/add/', admin_views.category_add, name='category-add'),
    path('categories/delete/<int:cid>/', admin_views.category_delete, name='category-delete'),
    path('categories/edit/<int:cid>/', admin_views.category_edit, name='category-edit'),
    path('subcategories/add/', admin_views.subcategory_add, name='subcategory-add'),
    path('subcategories/delete/<int:sid>/', admin_views.subcategory_delete, name='subcategory-delete'),
    path('subcategories/edit/<int:sid>/', admin_views.subcategory_edit, name='subcategory-edit'),
], 'useradmin')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin-panel/', include(useradmin_patterns)),
    path('', include('app.urls', namespace='carzo_core')),
    path('', include('userauths.urls', namespace='userauths')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)