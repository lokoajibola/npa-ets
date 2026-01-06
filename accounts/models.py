# accounts/models.py - ONLY User model
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):
    # Office/Role Choices based on NPA structure
    OFFICE_CHOICES = [
        ('executive_director', 'Executive Director'),
        ('general_manager', 'General Manager'),
        ('assistant_general_manager', 'Assistant General Manager'),
        ('chief_port_engineer', 'Chief Port Engineer'),
        ('unit_head', 'Unit Head'),
        ('engineer', 'Engineer'),
    ]
    
    # Grade Levels for Engineers
    GRADE_LEVEL_CHOICES = [
        (16, 'GL 16 - Director'),
        (15, 'GL 15 - Deputy Director'),
        (14, 'GL 14 - Assistant Director'),
        (13, 'GL 13 - Chief Engineer'),
        (12, 'GL 12 - Principal Engineer'),
        (10, 'GL 10 - Senior Engineer'),
        (9, 'GL 9 - Engineer I'),
        (8, 'GL 8 - Engineer II'),
    ]
    
    # Department Choices
    DEPARTMENT_CHOICES = [
        ('civil', 'Civil Engineering'),
        ('electrical', 'Electrical Engineering'),
        ('mechanical', 'Mechanical Engineering'),
        ('marine', 'Marine Engineering'),
        ('planning', 'Planning & Design'),
        ('maintenance', 'Maintenance'),
        ('dredging', 'Dredging'),
        ('environmental', 'Environmental Engineering'),
    ]
    
    # User fields
    office = models.CharField(max_length=50, choices=OFFICE_CHOICES, default='engineer')
    grade_level = models.IntegerField(choices=GRADE_LEVEL_CHOICES, null=True, blank=True)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    employee_id = models.CharField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=20)
    signature_pin = models.CharField(max_length=6, blank=True, null=True)
    pin_set = models.BooleanField(default=False)
    is_approving_officer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-grade_level', 'last_name']
    
    def __str__(self):
        return f"{self.get_full_name()} - {self.get_office_display()}"