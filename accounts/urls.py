from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Profile
    path('profile/', views.profile_view, name='profile'),
    
    # Settings
    path('settings/', views.settings_view, name='settings'),
    
    # Password change
    path('password/change/', views.change_password_view, name='password_change'),
    
    # User management (admin only)
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/create/', views.UserCreateView.as_view(), name='user_create'),
]