from django.shortcuts import render

# Create your views here.


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from userauths.models import User

def login_view(request):
    if request.user.is_authenticated:
        return redirect('carzo_core:dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            return redirect('carzo_core:dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'userauths/login.html')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('carzo_core:dashboard')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect('userauths:signup')
        
        # Create user
        user = User.objects.create_user(
            username=email,         # use email as username
            email=email,
            password=password,
            first_name=name.split()[0] if name else '',
            last_name=' '.join(name.split()[1:]) if name else '',
            phone=phone
        )
        login(request, user)
        return redirect('carzo_core:dashboard')
    
    return render(request, 'userauths/signup.html')


def logout_view(request):
    logout(request)
    return redirect('userauths:login')