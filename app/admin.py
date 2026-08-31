from django.contrib import admin

# Register your models here.

from django.contrib import admin
from app.models import Car, Category, SubCategory, CarOwner, Booking, CarListingRequest, ContactMessage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['category']


@admin.register(CarOwner)
class CarOwnerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'location']
    search_fields = ['name', 'phone']


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'category', 'fuel_type', 'passengers', 'price_per_day', 'is_available', 'car_image']
    list_filter = ['category', 'fuel_type', 'is_available']
    search_fields = ['name', 'brand']
    list_editable = ['is_available', 'price_per_day']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['bid', 'car', 'cust_name', 'cust_phone', 'pickup_date', 'drop_date', 'total_cost', 'booking_status', 'payment_status', 'created_at']
    list_filter = ['booking_status', 'payment_status', 'created_at']
    search_fields = ['bid', 'cust_name', 'cust_phone', 'car__name']
    list_editable = ['booking_status', 'payment_status']
    readonly_fields = ['bid', 'order_group_id', 'created_at']


@admin.register(CarListingRequest)
class CarListingRequestAdmin(admin.ModelAdmin):
    list_display = ['car_name', 'owner_name', 'phone', 'email', 'submitted_at', 'is_reviewed']
    list_editable = ['is_reviewed']
    list_filter = ['is_reviewed']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'submitted_at', 'is_read']
    list_editable = ['is_read']
    list_filter = ['is_read']