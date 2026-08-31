from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
import json
import re
import hmac
import hashlib
import time
import urllib.request

import razorpay
from razorpay.errors import SignatureVerificationError

from app.models import Car, Category, SubCategory, Booking, CarListingRequest, ContactMessage
from userauths.models import User



# RAZORPAY HELPERS

def get_razorpay_client():
    """
    Single shared Razorpay SDK client, authenticated with the key id/secret
    from settings (which come from RAZORPAY_KEY_ID / RAZORPAY_KEY_SECRET in .env).
    """
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def create_razorpay_order(amount_rupees, receipt):
    """
    Creates an Order on Razorpay's servers for the given amount (in rupees).
    This MUST happen server-side — it's the only way to guarantee the amount
    charged is the amount your backend calculated, not whatever a tampered
    client might send. Returns the order dict from Razorpay (contains 'id',
    'amount', 'currency', etc.) or raises on failure.
    """
    client = get_razorpay_client()
    amount_paise = int(round(float(amount_rupees) * 100))  # Razorpay works in the smallest currency unit
    return client.order.create({
        'amount': amount_paise,
        'currency': 'INR',
        'receipt': receipt,
        'payment_capture': 1,  # auto-capture the payment once authorized
    })


def verify_razorpay_payment(razorpay_order_id, razorpay_payment_id, razorpay_signature):
    """
    Verifies the HMAC-SHA256 signature Razorpay Checkout hands back after a
    successful payment. This is the step that actually proves the payment is
    genuine and wasn't spoofed by someone POSTing fake values to our endpoint.
    Returns True/False.
    """
    client = get_razorpay_client()
    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature,
        })
        return True
    except SignatureVerificationError:
        return False


def verify_razorpay_webhook_signature(request):
    """
    Verifies the X-Razorpay-Signature header on an incoming webhook request
    against the raw request body, using the webhook secret configured on the
    Razorpay dashboard (Settings > Webhooks). This proves the webhook call
    genuinely came from Razorpay and not from a third party.
    """
    webhook_secret = getattr(settings, 'RAZORPAY_WEBHOOK_SECRET', '')
    received_signature = request.headers.get('X-Razorpay-Signature', '')
    if not webhook_secret or not received_signature:
        return False
    expected_signature = hmac.new(
        key=webhook_secret.encode('utf-8'),
        msg=request.body,
        digestmod=hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected_signature, received_signature)



# HOME (index.html)

def index(request):
    cars = Car.objects.filter(is_available=True).order_by('-created_at')[:8]
    categories = Category.objects.all()
    context = {
        'cars': cars,
        'categories': categories,
    }
    return render(request, 'core/index.html', context)



# ALL CARS (cars.html)

def cars_list(request):
    cars = Car.objects.all()
    categories = Category.objects.prefetch_related('subcategories').all()
    
    # Filters from GET params (sent by search form)
    search = request.GET.get('search', '')
    category_name = request.GET.get('category', '')
    fuel = request.GET.get('fuel', '')
    max_price = request.GET.get('max_price', '')
    
    pickup_date_str = request.GET.get('pickup_date', '')
    pickup_time_str = request.GET.get('pickup_time', '')
    dropoff_date_str = request.GET.get('dropoff_date', '')
    dropoff_time_str = request.GET.get('dropoff_time', '')
    
    if pickup_date_str and dropoff_date_str:
        from datetime import date, time
        from django.db.models import Q
        
        p_date = None
        p_time = time(10, 0)
        d_date = None
        d_time = time(10, 0)
        
        try:
            p_date = date.fromisoformat(pickup_date_str)
        except ValueError:
            pass
            
        if pickup_time_str:
            try:
                parts = [int(x) for x in pickup_time_str.split(':')[:2]]
                p_time = time(parts[0], parts[1])
            except (ValueError, IndexError):
                pass
                
        try:
            d_date = date.fromisoformat(dropoff_date_str)
        except ValueError:
            pass
            
        if dropoff_time_str:
            try:
                parts = [int(x) for x in dropoff_time_str.split(':')[:2]]
                d_time = time(parts[0], parts[1])
            except (ValueError, IndexError):
                pass
                
        if p_date and d_date:
            overlap_condition = (
                (Q(pickup_date__lt=d_date) | Q(pickup_date=d_date, pickup_time__lt=d_time)) &
                (Q(drop_date__gt=p_date) | Q(drop_date=p_date, drop_time__gt=p_time)) &
                Q(booking_status__in=['Confirmed', 'Active', 'Delivered'])
            )
            booked_car_ids = Booking.objects.filter(overlap_condition).values_list('car_id', flat=True)
            cars = cars.exclude(id__in=booked_car_ids)
            
    if search:
        cars = cars.filter(
            name__icontains=search
        ) | cars.filter(brand__icontains=search) | cars.filter(fuel_type__icontains=search)
    
    if category_name:
        cars = cars.filter(category__name=category_name)
    
    if fuel:
        cars = cars.filter(fuel_type=fuel)
    
    if max_price:
        try:
            cars = cars.filter(price_per_day__lte=float(max_price))
        except ValueError:
            pass
    
    context = {
        'cars': cars,
        'categories': categories,
    }
    return render(request, 'core/cars.html', context)



# CAR DETAIL (car-detail.html)

def car_detail(request, cid):
    car = get_object_or_404(Car, cid=cid)
    context = {'car': car}
    return render(request, 'core/car-detail.html', context)



# BOOKING (booking.html)

def booking(request, cid):
    car = get_object_or_404(Car, cid=cid)

    if not car.is_available:
        messages.error(request, 'This car is currently unavailable.')
        return redirect('carzo_core:cars')

    if request.method == 'POST':
        action = request.POST.get('action', 'show_payment')

        # Read form values
        cust_name = request.POST.get('cust_name', '').strip()
        cust_phone = request.POST.get('cust_phone', '').strip()
        pickup_loc = request.POST.get('pickup_loc', '').strip()
        pickup_date = request.POST.get('pickup_date', '')
        drop_date = request.POST.get('drop_date', '')
        pickup_time = request.POST.get('pickup_time', '10:00')
        drop_time = request.POST.get('drop_time', '10:00')

        # Basic validation
        if not (cust_name and cust_phone and pickup_date and drop_date):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'core/booking.html', {'car': car, 'step': 1})

        # Compute total_days server-side from submitted dates
        from datetime import date as date_type
        try:
            pd = date_type.fromisoformat(pickup_date)
            dd = date_type.fromisoformat(drop_date)
            total_days = max((dd - pd).days, 1)
        except ValueError:
            total_days = 1

        subtotal = float(car.price_per_day) * total_days
        total_cost = subtotal

        if action == 'show_payment':
            # Create the Razorpay order NOW, server-side, using the total_cost
            # WE calculated above — never trust an amount posted from the browser.
            receipt = f'carzo-{car.cid}-{int(time.time())}'
            try:
                razorpay_order = create_razorpay_order(total_cost, receipt=receipt)
            except Exception as e:
                messages.error(request, f'Unable to start payment right now. Please try again. ({e})')
                return render(request, 'core/booking.html', {'car': car, 'step': 1})

            context = {
                'car': car,
                'step': 2,
                'cust_name': cust_name,
                'cust_phone': cust_phone,
                'pickup_loc': pickup_loc,
                'pickup_date': pickup_date,
                'drop_date': drop_date,
                'pickup_time': pickup_time,
                'drop_time': drop_time,
                'total_days': total_days,
                'total_cost': total_cost,
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_amount': razorpay_order['amount'],
            }
            return render(request, 'core/booking.html', context)

        elif action == 'complete_booking':
            user = request.user if request.user.is_authenticated else None
            cust_email = request.user.email if request.user.is_authenticated else ''

            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_signature = request.POST.get('razorpay_signature', '')

            payment_ok = bool(razorpay_order_id and razorpay_payment_id and razorpay_signature) and \
                verify_razorpay_payment(razorpay_order_id, razorpay_payment_id, razorpay_signature)

            if payment_ok:
                # Guard against the same successful payment creating two bookings
                # (e.g. a double form submit / back-button resubmit).
                booking_obj, created = Booking.objects.get_or_create(
                    order_group_id=razorpay_order_id,
                    defaults=dict(
                        car=car,
                        user=user,
                        cust_name=cust_name,
                        cust_phone=cust_phone,
                        cust_email=cust_email,
                        pickup_location=pickup_loc,
                        pickup_date=pickup_date,
                        pickup_time=pickup_time,
                        drop_date=drop_date,
                        drop_time=drop_time,
                        total_days=total_days,
                        subtotal=subtotal,
                        gst=0,
                        service_fee=0,
                        total_cost=total_cost,
                        booking_status='Confirmed',
                        payment_status='paid',
                        razorpay_payment_id=razorpay_payment_id,
                    ),
                )
                if not created and not booking_obj.razorpay_payment_id:
                    booking_obj.razorpay_payment_id = razorpay_payment_id
                    booking_obj.payment_status = 'paid'
                    booking_obj.save()

                return render(request, 'core/booking.html', {
                    'car': car,
                    'step': 3,
                    'booking': booking_obj,
                })
            else:
                return render(request, 'core/booking.html', {
                    'car': car,
                    'step': 4,
                    'failure_reason': 'We could not verify your payment. If any amount was deducted, it will be automatically refunded by Razorpay within 5-7 business days. No booking was created — please try again.',
                })

    # GET — show step 1
    return render(request, 'core/booking.html', {'car': car, 'step': 1})



# PAYMENT STATUS (return URL from Cashfree)

def payment_status(request):
    """
    Simple lookup page for a booking's payment status, kept for anyone who
    still has this URL. The real-time confirmation now happens synchronously
    in the booking() view right after Razorpay Checkout succeeds.
    """
    order_id = request.GET.get('order_id')
    booking_obj = Booking.objects.filter(order_group_id=order_id).first() if order_id else None
    if not booking_obj:
        return render(request, 'core/payment_status.html', {'status': 'error', 'message': 'Booking not found.'})
    status = 'success' if booking_obj.payment_status == 'paid' else 'failed'
    return render(request, 'core/payment_status.html', {'status': status, 'booking': booking_obj})


@csrf_exempt
@require_POST
def razorpay_webhook(request):
    """
    Server-to-server webhook Razorpay calls directly (not via the customer's
    browser). This is a production best practice on top of the client-side
    verification in booking(): it catches cases where a payment succeeds but
    the customer's browser closes/crashes before the success handler runs,
    so the booking would otherwise never get marked paid.

    Configure this URL in the Razorpay Dashboard under
    Settings > Webhooks, e.g. https://yourdomain.com/razorpay-webhook/
    Subscribe at least to the 'payment.captured' and 'payment.failed' events,
    and set RAZORPAY_WEBHOOK_SECRET in .env to the secret shown there.
    """
    if not verify_razorpay_webhook_signature(request):
        return HttpResponseBadRequest('Invalid webhook signature')

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (ValueError, UnicodeDecodeError):
        return HttpResponseBadRequest('Invalid payload')

    event = payload.get('event', '')
    payment_entity = payload.get('payload', {}).get('payment', {}).get('entity', {})
    razorpay_order_id = payment_entity.get('order_id')
    razorpay_payment_id = payment_entity.get('id')

    if razorpay_order_id:
        booking_obj = Booking.objects.filter(order_group_id=razorpay_order_id).first()
        if booking_obj:
            if event == 'payment.captured':
                booking_obj.payment_status = 'paid'
                if razorpay_payment_id:
                    booking_obj.razorpay_payment_id = razorpay_payment_id
                booking_obj.save()
            elif event == 'payment.failed':
                # Only downgrade if we haven't already recorded a successful
                # payment for this order via the synchronous flow.
                if booking_obj.payment_status != 'paid':
                    booking_obj.payment_status = 'failed'
                    booking_obj.save()

    # Always return 200 quickly so Razorpay doesn't keep retrying.
    return HttpResponse('ok')



# DASHBOARD (dashboard.html)

@login_required
def dashboard(request):
    bookings = Booking.objects.filter(user=request.user)
    total_bookings = bookings.count()
    active_bookings = bookings.filter(booking_status__in=['Confirmed', 'Active', 'Delivered']).count()
    completed_trips = bookings.filter(booking_status='Completed').count()
    total_spent = sum(
        b.total_cost for b in bookings.exclude(booking_status='Cancelled')
    )
    recent_bookings = bookings.filter(booking_status__in=['Confirmed', 'Active', 'Delivered'])[:3]
    
    context = {
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'active_rentals': active_bookings,
        'completed_trips': completed_trips,
        'total_spent': total_spent,
        'recent_bookings': recent_bookings,
        'active_or_upcoming': recent_bookings,
    }
    return render(request, 'core/dashboard.html', context)



# BOOKING MANAGEMENT (booking-management.html)

@login_required
def booking_management(request):
    filter_type = request.GET.get('filter', 'all')
    bookings = Booking.objects.filter(user=request.user)
    
    if filter_type == 'active':
        bookings = bookings.filter(booking_status__in=['Confirmed', 'Active', 'Delivered'])
    elif filter_type == 'completed':
        bookings = bookings.filter(booking_status='Completed')
    elif filter_type == 'cancelled':
        bookings = bookings.filter(booking_status='Cancelled')
    
    context = {
        'bookings': bookings,
        'filter_type': filter_type,
    }
    return render(request, 'core/booking-management.html', context)


@login_required
def my_booking_detail(request, bid):
    booking_obj = get_object_or_404(Booking, bid=bid, user=request.user)
    context = {
        'booking': booking_obj,
    }
    return render(request, 'core/booking-detail.html', context)


@login_required
def modify_booking(request, bid):
    booking_obj = get_object_or_404(Booking, bid=bid, user=request.user)
    if booking_obj.booking_status not in ['Confirmed', 'Active']:
        messages.error(request, 'This booking cannot be modified.')
        return redirect('carzo_core:booking-management')
        
    if request.method == 'POST':
        pickup_date = request.POST.get('pickup_date')
        drop_date = request.POST.get('drop_date')
        total_days = request.POST.get('total_days')
        total_cost = request.POST.get('total_cost')
        
        if pickup_date and drop_date:
            booking_obj.pickup_date = pickup_date
            booking_obj.drop_date = drop_date
            if total_days:
                booking_obj.total_days = int(total_days)
            if total_cost:
                booking_obj.total_cost = float(total_cost)
            booking_obj.save()
            messages.success(request, 'Booking dates updated successfully.')
        else:
            messages.error(request, 'Invalid date selection.')
            
    return redirect('carzo_core:booking-management')


@login_required
def cancel_booking(request, bid):
    booking_obj = get_object_or_404(Booking, bid=bid, user=request.user)
    
    if booking_obj.booking_status in ['Confirmed', 'Active']:
        booking_obj.booking_status = 'Cancelled'
        booking_obj.save()
        messages.success(request, 'Booking cancelled successfully.')
    else:
        messages.error(request, 'This booking cannot be cancelled.')
    
    return redirect('carzo_core:booking-management')



# PROFILE (profile.html)

@login_required
def profile(request):
    if request.method == 'POST':
        user = request.user
        full_name = request.POST.get('full_name')
        if full_name:
            parts = full_name.strip().split(' ', 1)
            user.first_name = parts[0]
            user.last_name = parts[1] if len(parts) > 1 else ''
        user.phone = request.POST.get('phone', user.phone)
        
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
        
        user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('carzo_core:profile')
    
    return render(request, 'core/profile.html', {'user': request.user})



# LIST YOUR CAR (list-car.html)

def list_car(request):
    if request.method == 'POST':
        CarListingRequest.objects.create(
            owner_name=request.POST.get('owner_name'),
            phone=request.POST.get('phone'),
            email=request.POST.get('email'),
            car_name=request.POST.get('car_name'),
            car_year=request.POST.get('car_year', ''),
            car_description=request.POST.get('car_description', ''),
        )
        messages.success(request, 'Your car listing request has been submitted. We will contact you shortly.')
        return redirect('carzo_core:list-car')
    
    return render(request, 'core/list-car.html')



# CONTACT (contact.html)

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        message = request.POST.get('message')
        
        ContactMessage.objects.create(
            name=name,
            email=email,
            phone=phone,
            message=message,
        )
        
        try:
            send_mail(
                subject=f'New Contact Message from {name}',
                message=f'Name: {name}\nEmail: {email}\nPhone: {phone}\n\nMessage:\n{message}',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=True,
            )
        except Exception:
            pass
        
        messages.success(request, 'Message sent successfully!')
        return redirect('carzo_core:contact')
    
    return render(request, 'core/contact.html')



# STATIC INFO PAGES

def about(request):
    return render(request, 'core/about.html')