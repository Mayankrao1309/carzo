from django.db import models

# Create your models here.


from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from userauths.models import User
import re
from django.utils import timezone


def owner_image_path(instance, filename):
    return f'owners/{instance.id}/{filename}'


def car_image_path(instance, filename):
    return f'cars/{instance.id}/{filename}'


# ── Categories ──────────────────────────────────────────────
class Category(models.Model):
    """Matches Carzo's parent categories (e.g. Luxury, SUV, Sedan)"""
    name = models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name


class SubCategory(models.Model):
    """Matches Carzo's subcategory filters"""
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    
    class Meta:
        verbose_name_plural = 'SubCategories'
    
    def __str__(self):
        return f'{self.category.name} > {self.name}'


# ── Car Owner / Host ──────────────────────────────────────────
class CarOwner(models.Model):
    """
    Represents a car host. 
    Carzo frontend shows owner name, phone, email, hub on car-detail.html.
    """
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    location = models.CharField(max_length=100, default='Pune Hub')
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


# ── Car ────────────────────────────────────────────────────────
FUEL_TYPE_CHOICES = (
    ('Petrol', 'Petrol'),
    ('Diesel', 'Diesel'),
    ('Electric', 'Electric'),
    ('CNG', 'CNG'),
)

class Car(models.Model):
    """
    Core car listing.
    Maps to Carzo frontend: cars.html, car-detail.html, booking.html
    """
    cid = ShortUUIDField(unique=True, length=50, alphabet='1234567890abcdef')
    name = models.CharField(max_length=200)          # Display name e.g. "Tesla Model Y"
    brand = models.CharField(max_length=100)         # Brand only e.g. "Tesla"
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True)
    subcategories = models.ManyToManyField(SubCategory, blank=True, related_name='cars')
    
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPE_CHOICES, default='Petrol')
    passengers = models.PositiveIntegerField(default=5)
    
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    price_weekend = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_per_month = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    image = models.ImageField(upload_to=car_image_path)
    image2 = models.ImageField(upload_to=car_image_path, blank=True, null=True)
    image3 = models.ImageField(upload_to=car_image_path, blank=True, null=True)
    image4 = models.ImageField(upload_to=car_image_path, blank=True, null=True)
    
    is_available = models.BooleanField(default=True)
    owner = models.ForeignKey(CarOwner, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Cars'
        ordering = ['-created_at']

    def car_image(self):
        return mark_safe(f'<img src="{self.image.url}" width="60" height="40" style="object-fit:cover"/>')

    def get_weekend_price(self):
        return self.price_weekend or self.price_per_day

    def __str__(self):
        return self.name

    @property
    def car_id(self):
        return self.cid

    @property
    def model(self):
        if self.name.startswith(self.brand):
            return self.name[len(self.brand):].strip()
        return self.name

    @property
    def price_day(self):
        return self.price_per_day

    @property
    def price_month(self):
        return self.price_per_month or 0

    @property
    def is_placeholder(self):
        return False

    @property
    def color_code(self):
        return '#2c3e50'

    @property
    def available(self):
        return self.is_available


# ── Car Listing Request (list-car.html form) ──────────────────
class CarListingRequest(models.Model):
    """
    Submitted by users who want to list their car.
    Carzo's list-car.html form captures this.
    """
    owner_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    car_name = models.CharField(max_length=200)
    car_year = models.CharField(max_length=10)
    car_description = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_reviewed = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.car_name} by {self.owner_name}'


# ── Booking ────────────────────────────────────────────────────
BOOKING_STATUS_CHOICES = (
    ('Confirmed', 'Confirmed'),
    ('Active', 'Active'),
    ('Delivered', 'Delivered'),
    ('Completed', 'Completed'),
    ('Cancelled', 'Cancelled'),
)

PAYMENT_STATUS_CHOICES = (
    ('paid', 'Paid'),
    ('not_paid', 'Not Paid'),
    ('failed', 'Failed'),
)

class Booking(models.Model):
    """
    Core booking model.
    Maps to booking.html (create), booking-management.html (list/cancel), dashboard.html (stats).
    """
    bid = models.CharField(max_length=20, unique=True, blank=True, editable=False)
    order_group_id = models.CharField(max_length=100, null=True, blank=True)  # Razorpay order ID (order_...)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)  # Razorpay payment ID (pay_...)
    
    car = models.ForeignKey(Car, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Customer details (stored at time of booking, works for guests too)
    cust_name = models.CharField(max_length=100)
    cust_phone = models.CharField(max_length=20)
    cust_email = models.EmailField(blank=True, null=True)
    
    pickup_location = models.CharField(max_length=200)
    pickup_date = models.DateField()
    pickup_time = models.TimeField()
    drop_date = models.DateField()
    drop_time = models.TimeField()
    
    total_days = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    service_fee = models.DecimalField(max_digits=6, decimal_places=2, default=250)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    booking_status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default='Confirmed')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='not_paid')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Bookings'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.bid:
            now = timezone.now()
            prefix = 'BD'
            import random, string
            suffix = ''.join(random.choices(string.digits, k=6))
            self.bid = f'{prefix}-{suffix}'
        super().save(*args, **kwargs)

    def __str__(self):
        car_name = self.car.name if self.car else 'Unknown Car'
        return f'Booking {self.bid} - {car_name}'

    @property
    def booking_id(self):
        return self.bid

    @property
    def pickup_loc(self):
        return self.pickup_location

    @property
    def status(self):
        return self.booking_status

    @property
    def date_created(self):
        return self.created_at


# ── Contact Message ───────────────────────────────────────────
class ContactMessage(models.Model):
    """Captures contact.html form submission"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'Message from {self.name}'
