from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum
from django.urls import reverse
from app.models import Car, Category, SubCategory, Booking, CarOwner, ContactMessage
from userauths.models import User

def staff_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to access the Admin Panel.")
            return redirect('userauths:login')
        if not request.user.is_staff:
            messages.error(request, "You are not authorized to view this page.")
            return redirect('carzo_core:index')
        return view_func(request, *args, **kwargs)
    return wrapper

@staff_required
def admin_panel(request):
    total_bookings = Booking.objects.count()
    total_revenue = Booking.objects.exclude(booking_status='Cancelled').aggregate(Sum('total_cost'))['total_cost__sum'] or 0
    total_customers = User.objects.filter(is_staff=False).count()
    
    recent_bookings = Booking.objects.all().order_by('-created_at')[:5]
    recent_customers = User.objects.filter(is_staff=False).order_by('-date_joined')[:5]
    
    admins = User.objects.filter(is_staff=True).order_by('email')
    customers = User.objects.filter(is_staff=False).order_by('email')
    bookings = Booking.objects.all().order_by('-created_at')
    cars = Car.objects.all().order_by('-created_at')
    owners = CarOwner.objects.all().order_by('name')
    categories = Category.objects.all().order_by('name')
    subcategories = SubCategory.objects.all().order_by('name')
    
    active_tab = request.GET.get('tab', 'dashboard')
    
    context = {
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'total_customers': total_customers,
        'recent_bookings': recent_bookings,
        'recent_customers': recent_customers,
        'admins': admins,
        'customers': customers,
        'bookings': bookings,
        'cars': cars,
        'owners': owners,
        'categories': categories,
        'subcategories': subcategories,
        'active_tab': active_tab,
    }
    return render(request, 'useradmin/admin.html', context)

@staff_required
def admin_add(request):
    if request.method == 'POST':
        user_id = request.POST.get('customer_id', '').strip()
        role = request.POST.get('role', 'Staff Admin').strip()

        if not user_id:
            messages.error(request, "Please select a customer to promote.")
            return redirect(reverse('useradmin:admin-panel') + '?tab=admins')

        try:
            user = User.objects.get(id=user_id, is_staff=False)
        except User.DoesNotExist:
            messages.error(request, "Selected customer not found or is already an admin.")
            return redirect(reverse('useradmin:admin-panel') + '?tab=admins')

        user.is_staff = True
        # Store role in last_name as a lightweight label (no schema change needed)
        user.last_name = role
        if role == 'Super Admin':
            user.is_superuser = True
        user.save()
        name = user.first_name or user.email
        messages.success(request, f"{name} has been promoted to Admin ({role}) successfully.")
    return redirect(reverse('useradmin:admin-panel') + '?tab=admins')

@staff_required
def admin_delete(request, uid):
    user = get_object_or_404(User, id=uid)
    if user == request.user:
        messages.error(request, "You cannot remove yourself from admin.")
    else:
        name = user.first_name or user.email
        user.is_staff = False
        user.is_superuser = False
        user.last_name = ''
        user.save()
        messages.success(request, f"{name} has been removed from admin and restored to the customer list.")
    return redirect(reverse('useradmin:admin-panel') + '?tab=admins')

@staff_required
def admin_edit(request, uid):
    if request.method == 'POST':
        user = get_object_or_404(User, id=uid, is_staff=True)
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        role = request.POST.get('role', '').strip()

        if name:
            user.first_name = name
        if phone:
            user.phone = phone
        user.last_name = role
        user.is_superuser = (role == 'Super Admin')
        user.save()
        messages.success(request, f"Admin member '{user.first_name or user.email}' updated successfully.")
    return redirect(reverse('useradmin:admin-panel') + '?tab=admins')

@staff_required
def owner_save(request):
    if request.method == 'POST':
        mode = request.POST.get('mode', 'add')
        owner_id = request.POST.get('owner_id')
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        location = request.POST.get('location', '').strip()
        
        dup_query = CarOwner.objects.filter(name__iexact=name)
        if mode == 'edit':
            dup_query = dup_query.exclude(id=owner_id)
            
        if dup_query.exists():
            messages.error(request, f"An owner with the name '{name}' already exists.")
            return redirect(reverse('useradmin:admin-panel') + '?tab=owners')
            
        if mode == 'edit':
            owner = get_object_or_404(CarOwner, id=owner_id)
            owner.name = name
            owner.email = email
            owner.phone = phone
            owner.location = location
            owner.save()
            messages.success(request, f"Owner '{name}' updated successfully.")
        else:
            CarOwner.objects.create(name=name, email=email, phone=phone, location=location)
            messages.success(request, f"Owner '{name}' added successfully.")
            
    return redirect(reverse('useradmin:admin-panel') + '?tab=owners')

@staff_required
def owner_delete(request, oid):
    owner = get_object_or_404(CarOwner, id=oid)
    if Car.objects.filter(owner=owner).exists():
        messages.error(request, f"Cannot delete owner '{owner.name}' because they have cars assigned.")
    else:
        name = owner.name
        owner.delete()
        messages.success(request, f"Owner '{name}' deleted successfully.")
    return redirect(reverse('useradmin:admin-panel') + '?tab=owners')

@staff_required
def car_save(request):
    if request.method == 'POST':
        mode = request.POST.get('mode', 'add')
        car_id = request.POST.get('car_id')
        
        brand = request.POST.get('brand', '').strip()
        model = request.POST.get('model', '').strip()
        price_day = request.POST.get('price_day')
        price_month = request.POST.get('price_month')
        price_weekend = request.POST.get('price_weekend')
        passengers = request.POST.get('passengers', 5)
        fuel_type = request.POST.get('fuel_type', 'Petrol')
        owner_name = request.POST.get('owner')
        is_available = request.POST.get('available') == 'on' or request.POST.get('available') == 'true'
        
        # Collect subcategory IDs from dynamic per-category dropdowns (cat_<id> fields)
        selected_sub_ids = []
        for key, value in request.POST.items():
            if key.startswith('cat_') and value:
                try:
                    selected_sub_ids.append(int(value))
                except ValueError:
                    pass
        
        selected_subcategories = SubCategory.objects.filter(id__in=selected_sub_ids)
        
        # Auto-set legacy FK fields from the first selected subcategory's category
        legacy_category = None
        legacy_subcategory = None
        if selected_subcategories.exists():
            first_sub = selected_subcategories.first()
            legacy_category = first_sub.category
            legacy_subcategory = first_sub
            
        owner = CarOwner.objects.filter(name=owner_name).first()
        
        p_wknd = float(price_weekend) if price_weekend else float(price_day)
        p_mon = float(price_month) if price_month else None
        
        name = f"{brand} {model}"
        
        if mode == 'edit':
            car = get_object_or_404(Car, cid=car_id)
            car.name = name
            car.brand = brand
            car.category = legacy_category
            car.subcategory = legacy_subcategory
            car.price_per_day = float(price_day)
            car.price_weekend = p_wknd
            car.price_per_month = p_mon
            car.passengers = int(passengers)
            car.fuel_type = fuel_type
            car.owner = owner
            car.is_available = is_available
            
            if 'image' in request.FILES:
                car.image = request.FILES['image']
            if 'image2' in request.FILES:
                car.image2 = request.FILES['image2']
            if 'image3' in request.FILES:
                car.image3 = request.FILES['image3']
            if 'image4' in request.FILES:
                car.image4 = request.FILES['image4']
                
            car.save()
            car.subcategories.set(selected_subcategories)
            messages.success(request, f"Vehicle '{name}' updated successfully.")
        else:
            image = request.FILES.get('image')
            if not image:
                messages.error(request, "Primary display image is required for listing new vehicles.")
                return redirect(reverse('useradmin:admin-panel') + '?tab=cars')
                
            car = Car.objects.create(
                name=name,
                brand=brand,
                category=legacy_category,
                subcategory=legacy_subcategory,
                price_per_day=float(price_day),
                price_weekend=p_wknd,
                price_per_month=p_mon,
                passengers=int(passengers),
                fuel_type=fuel_type,
                owner=owner,
                is_available=is_available,
                image=image,
                image2=request.FILES.get('image2'),
                image3=request.FILES.get('image3'),
                image4=request.FILES.get('image4')
            )
            car.subcategories.set(selected_subcategories)
            messages.success(request, f"Vehicle '{name}' added successfully.")
            
    return redirect(reverse('useradmin:admin-panel') + '?tab=cars')


@staff_required
def car_delete(request, cid):
    car = get_object_or_404(Car, cid=cid)
    name = car.name
    car.delete()
    messages.success(request, f"Vehicle '{name}' removed successfully.")
    return redirect(reverse('useradmin:admin-panel') + '?tab=cars')

@staff_required
def car_toggle_availability(request, cid):
    car = get_object_or_404(Car, cid=cid)
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            available = data.get('available', False)
        except Exception:
            available = request.POST.get('available') == 'true' or request.POST.get('available') == 'on'
            
        car.is_available = available
        car.save()
        return JsonResponse({'success': True, 'is_available': car.is_available})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)

@staff_required
def booking_detail_json(request, bid):
    booking = get_object_or_404(Booking, bid=bid)
    data = {
        'id': booking.bid,
        'status': booking.booking_status,
        'dateCreated': booking.created_at.strftime('%Y-%m-%d %H:%M'),
        'custName': booking.cust_name,
        'custEmail': booking.cust_email,
        'custPhone': booking.cust_phone,
        'pickupLoc': booking.pickup_location,
        'carName': booking.car.name if booking.car else 'Unknown Car',
        'pickupDate': booking.pickup_date.strftime('%Y-%m-%d'),
        'pickupTime': booking.pickup_time.strftime('%H:%M'),
        'dropDate': booking.drop_date.strftime('%Y-%m-%d'),
        'dropTime': booking.drop_time.strftime('%H:%M'),
        'totalDays': booking.total_days,
        'totalCost': float(booking.total_cost),
    }
    return JsonResponse(data)

@staff_required
def booking_toggle_delivery(request, bid):
    booking = get_object_or_404(Booking, bid=bid)
    if request.method == 'POST':
        if booking.booking_status == 'Cancelled':
            return JsonResponse({'success': False, 'message': 'Cancelled bookings cannot be modified.'}, status=400)
        import json
        try:
            data = json.loads(request.body)
            delivered = data.get('delivered', False)
        except Exception:
            delivered = request.POST.get('delivered') == 'true' or request.POST.get('delivered') == 'on'
            
        booking.booking_status = 'Delivered' if delivered else 'Confirmed'
        booking.save()
        return JsonResponse({'success': True, 'status': booking.booking_status})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)


@staff_required
def category_add(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if Category.objects.filter(name__iexact=name).exists():
            messages.error(request, f"Category '{name}' already exists.")
        else:
            Category.objects.create(name=name)
            messages.success(request, f"Category '{name}' created successfully.")
    return redirect(reverse('useradmin:admin-panel') + '?tab=categories')

@staff_required
def subcategory_add(request):
    if request.method == 'POST':
        parent_name = request.POST.get('parent')
        name = request.POST.get('name', '').strip()
        category = Category.objects.filter(name=parent_name).first()
        
        if not category:
            messages.error(request, "Selected parent category not found.")
        elif SubCategory.objects.filter(category=category, name__iexact=name).exists():
            messages.error(request, f"Subcategory '{name}' already exists under '{parent_name}'.")
        else:
            SubCategory.objects.create(category=category, name=name)
            messages.success(request, f"Subcategory '{name}' mapped under '{parent_name}' successfully.")
    return redirect(reverse('useradmin:admin-panel') + '?tab=categories')

@staff_required
def category_delete(request, cid):
    category = get_object_or_404(Category, id=cid)
    name = category.name
    category.delete()
    messages.success(request, f"Category '{name}' and its related subcategories deleted successfully.")
    return redirect(reverse('useradmin:admin-panel') + '?tab=categories')

@staff_required
def subcategory_delete(request, sid):
    subcategory = get_object_or_404(SubCategory, id=sid)
    name = subcategory.name
    parent_name = subcategory.category.name
    subcategory.delete()
    messages.success(request, f"Subcategory '{name}' deleted successfully.")
    return redirect(reverse('useradmin:admin-panel') + '?tab=categories')

@staff_required
def category_edit(request, cid):
    category = get_object_or_404(Category, id=cid)
    if request.method == 'POST':
        new_name = request.POST.get('name', '').strip()
        if not new_name:
            messages.error(request, "Category name cannot be empty.")
        elif Category.objects.filter(name__iexact=new_name).exclude(id=cid).exists():
            messages.error(request, f"Category '{new_name}' already exists.")
        else:
            old_name = category.name
            category.name = new_name
            category.save()
            messages.success(request, f"Category renamed from '{old_name}' to '{new_name}'.")
    return redirect(reverse('useradmin:admin-panel') + '?tab=categories')

@staff_required
def subcategory_edit(request, sid):
    subcategory = get_object_or_404(SubCategory, id=sid)
    if request.method == 'POST':
        new_name = request.POST.get('name', '').strip()
        new_parent = request.POST.get('parent', '').strip()
        if not new_name:
            messages.error(request, "Subcategory name cannot be empty.")
        else:
            old_name = subcategory.name
            subcategory.name = new_name
            if new_parent:
                parent_cat = Category.objects.filter(name=new_parent).first()
                if parent_cat:
                    subcategory.category = parent_cat
            subcategory.save()
            messages.success(request, f"Subcategory '{old_name}' updated to '{new_name}'.")
    return redirect(reverse('useradmin:admin-panel') + '?tab=categories')
