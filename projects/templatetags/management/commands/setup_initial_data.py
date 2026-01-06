from django.core.management.base import BaseCommand
from accounts.models import User
from projects.models import Project, ProjectStage
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Setup initial data for NPA Projects Management System'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Setting up initial data...')
        
        # Create sample users with NPA hierarchy
        users_data = [
            {
                'username': 'ed_engineering',
                'email': 'ed.engineering@npa.gov.ng',
                'first_name': 'John',
                'last_name': 'Adebayo',
                'office': 'executive_director',
                'grade_level': 16,
                'department': 'civil',
                'employee_id': 'NPA/ENG/001',
                'phone_number': '08012345678',
                'is_staff': True,
            },
            {
                'username': 'gm_engineering',
                'email': 'gm.engineering@npa.gov.ng',
                'first_name': 'Musa',
                'last_name': 'Bello',
                'office': 'general_manager',
                'grade_level': 15,
                'department': 'electrical',
                'employee_id': 'NPA/ENG/002',
                'phone_number': '08012345679',
                'is_staff': True,
            },
            {
                'username': 'agm_civil',
                'email': 'agm.civil@npa.gov.ng',
                'first_name': 'Chinwe',
                'last_name': 'Okoro',
                'office': 'assistant_general_manager',
                'grade_level': 14,
                'department': 'civil',
                'employee_id': 'NPA/ENG/003',
                'phone_number': '08012345680',
                'is_staff': True,
            },
            {
                'username': 'chief_engineer',
                'email': 'chief.engineer@npa.gov.ng',
                'first_name': 'Amina',
                'last_name': 'Suleiman',
                'office': 'chief_port_engineer',
                'grade_level': 13,
                'department': 'mechanical',
                'employee_id': 'NPA/ENG/004',
                'phone_number': '08012345681',
                'is_staff': True,
            },
            {
                'username': 'engineer_1',
                'email': 'engineer1@npa.gov.ng',
                'first_name': 'Emeka',
                'last_name': 'Nwosu',
                'office': 'engineer',
                'grade_level': 10,
                'department': 'civil',
                'employee_id': 'NPA/ENG/005',
                'phone_number': '08012345682',
                'is_staff': True,
            },
        ]
        
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults=user_data
            )
            if created:
                user.set_password('password123')  # Change in production!
                user.save()
                self.stdout.write(f'Created user: {user.username}')
        
        self.stdout.write(self.style.SUCCESS('Initial data setup complete!'))