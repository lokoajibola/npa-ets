from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import User
from .forms import CustomUserCreationForm, UserProfileForm, PinForm

# Custom Login View with NPA branding
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'NPA Engineering - Login'
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Welcome back, {self.request.user.get_full_name()}!')
        return response

# User Profile View
@login_required
def profile_view(request):
    user = request.user
    
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, instance=user)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        profile_form = UserProfileForm(instance=user)
    
    context = {
        'profile_form': profile_form,
        'page_title': 'My Profile',
    }
    return render(request, 'accounts/profile.html', context)

# Settings View (PIN Setup)
@login_required
def settings_view(request):
    user = request.user
    
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = UserProfileForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('settings')
        
        elif 'set_pin' in request.POST:
            pin_form = PinForm(request.POST)
            if pin_form.is_valid():
                if user.pin_set:
                    # Verify current pin first
                    if pin_form.cleaned_data['current_pin'] != user.signature_pin:
                        messages.error(request, 'Current PIN is incorrect')
                        return redirect('settings')
                
                user.signature_pin = pin_form.cleaned_data['new_pin']
                user.pin_set = True
                user.save()
                messages.success(request, 'PIN set successfully!')
                return redirect('settings')
    
    else:
        profile_form = UserProfileForm(instance=user)
        pin_form = PinForm()
    
    context = {
        'profile_form': profile_form,
        'pin_form': pin_form,
        'page_title': 'Settings',
    }
    return render(request, 'settings/settings.html', context)

# User Management Views (Admin only)
class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    
    def get_queryset(self):
        # Only show users if the current user is admin or management
        if self.request.user.is_superuser or self.request.user.office in ['executive_director', 'general_manager']:
            return User.objects.all().order_by('-date_joined')
        return User.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'User Management'
        return context

class UserCreateView(LoginRequiredMixin, CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('user_list')
    
    def dispatch(self, request, *args, **kwargs):
        # Only allow admin and management to create users
        if not (request.user.is_superuser or request.user.office in ['executive_director', 'general_manager']):
            messages.error(request, "You don't have permission to create users.")
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        # Set default password (user should change on first login)
        user = form.save(commit=False)
        user.set_password('NPA@2024')  # Default password
        user.save()
        messages.success(self.request, f'User {user.username} created successfully!')
        return super().form_valid(form)

# Password Change View
@login_required
def change_password_view(request):
    from django.contrib.auth.forms import PasswordChangeForm
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Your password was successfully updated!')
            return redirect('settings')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
        'page_title': 'Change Password',
    }
    return render(request, 'accounts/change_password.html', context)