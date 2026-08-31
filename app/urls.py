from django.urls import path
from app import views

app_name = 'carzo_core'

urlpatterns = [
    path('', views.index, name='index'),
    path('cars/', views.cars_list, name='cars'),
    path('cars/<cid>/', views.car_detail, name='car_detail'),
    path('booking/<cid>/', views.booking, name='booking'),
    path('payment-status/', views.payment_status, name='payment_status'),
    path('razorpay-webhook/', views.razorpay_webhook, name='razorpay-webhook'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('my-bookings/', views.booking_management, name='booking-management'),
    path('my-bookings/details/<str:bid>/', views.my_booking_detail, name='booking-detail'),
    path('booking-management/modify/<str:bid>/', views.modify_booking, name='modify-booking'),
    path('booking-management/cancel/<str:bid>/', views.cancel_booking, name='cancel-booking'),
    path('profile/', views.profile, name='profile'),
    path('list-car/', views.list_car, name='list-car'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
]