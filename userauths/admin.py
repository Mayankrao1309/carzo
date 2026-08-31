from django.contrib import admin

# Register your models here.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from userauths.models import User

class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'get_full_name', 'phone', 'is_staff', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering = ['-date_joined']
    fieldsets = UserAdmin.fieldsets + (
        ('Carzo Fields', {'fields': ('phone', 'avatar')}),
    )

admin.site.register(User, CustomUserAdmin)