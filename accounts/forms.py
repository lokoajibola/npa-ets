from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',
                 'office', 'grade_level', 'department', 'employee_id',
                 'phone_number')
        widgets = {
            'grade_level': forms.Select(choices=User.GRADE_LEVEL_CHOICES),
            'office': forms.Select(choices=User.OFFICE_CHOICES),
            'department': forms.Select(choices=User.DEPARTMENT_CHOICES),
        }

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',
                 'office', 'grade_level', 'department', 'employee_id',
                 'phone_number')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'department')

class PinForm(forms.ModelForm):
    current_pin = forms.CharField(
        max_length=6, 
        required=False, 
        widget=forms.PasswordInput(attrs={'placeholder': 'Current PIN'}),
        label="Current PIN (if already set)"
    )
    new_pin = forms.CharField(
        max_length=6, 
        widget=forms.PasswordInput(attrs={'placeholder': '6-digit PIN'}),
        label="New PIN"
    )
    confirm_pin = forms.CharField(
        max_length=6, 
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm PIN'}),
        label="Confirm PIN"
    )
    
    class Meta:
        model = User
        fields = []
    
    def clean(self):
        cleaned_data = super().clean()
        new_pin = cleaned_data.get('new_pin')
        confirm_pin = cleaned_data.get('confirm_pin')
        
        if new_pin != confirm_pin:
            raise forms.ValidationError("PINs do not match")
        
        if len(new_pin) != 6 or not new_pin.isdigit():
            raise forms.ValidationError("PIN must be exactly 6 digits")
        
        return cleaned_data

# Simplified password change form
class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Current password'}),
        label="Current Password"
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'New password'}),
        label="New Password"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm new password'}),
        label="Confirm New Password"
    )