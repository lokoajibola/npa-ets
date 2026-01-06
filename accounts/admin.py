
# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 
                   'office', 'grade_level', 'department', 'is_staff')
    list_filter = ('office', 'grade_level', 'department', 'is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 
                                     'phone_number', 'employee_id')}),
        ('NPA Details', {'fields': ('office', 'grade_level', 'department',
                                   'signature_pin', 'pin_set')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                   'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2',
                      'first_name', 'last_name', 'phone_number', 'employee_id',
                      'office', 'grade_level', 'department'),
        }),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name', 'employee_id')
    ordering = ('-grade_level', 'last_name')