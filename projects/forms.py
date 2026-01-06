from django import forms
from django.utils import timezone
from .models import Project, ProjectStage, ProjectDocument, ProgressReport

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'title', 'description', 'project_type', 'location', 'port_location',
            'estimated_budget', 'proposed_start_date', 'proposed_end_date',
            'priority', 'project_manager', 'supervisor'
        ]
        widgets = {
            'proposed_start_date': forms.DateInput(attrs={'type': 'date'}),
            'proposed_end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Project description...'}),
        }
        labels = {
            'estimated_budget': 'Estimated Budget (₦)',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('proposed_start_date')
        end_date = cleaned_data.get('proposed_end_date')
        
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Start date cannot be after end date")
        
        if start_date and start_date < timezone.now().date():
            raise forms.ValidationError("Start date cannot be in the past")
        
        return cleaned_data

class ProjectStageForm(forms.ModelForm):
    class Meta:
        model = ProjectStage
        fields = ['status', 'start_date', 'end_date', 'assigned_to', 
                 'contractor', 'contract_reference', 'contract_date',
                 'document', 'notes']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'contract_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Stage notes...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter users based on role for assignment
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.fields['assigned_to'].queryset = User.objects.filter(
            office='engineer'
        ).order_by('first_name')

class ProjectDocumentForm(forms.ModelForm):
    class Meta:
        model = ProjectDocument
        fields = ['document_type', 'title', 'description', 'file']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Document description...'}),
        }

class ProgressReportForm(forms.ModelForm):
    class Meta:
        model = ProgressReport
        fields = ['report_date', 'period_start', 'period_end',
                 'percentage_complete', 'work_accomplished', 'challenges',
                 'next_activities']
        widgets = {
            'report_date': forms.DateInput(attrs={'type': 'date'}),
            'period_start': forms.DateInput(attrs={'type': 'date'}),
            'period_end': forms.DateInput(attrs={'type': 'date'}),
            'work_accomplished': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe work accomplished...'}),
            'challenges': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe challenges faced...'}),
            'next_activities': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe next activities...'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        period_start = cleaned_data.get('period_start')
        period_end = cleaned_data.get('period_end')
        percentage = cleaned_data.get('percentage_complete')
        
        if period_start and period_end and period_start > period_end:
            raise forms.ValidationError("Period start cannot be after period end")
        
        if percentage and (percentage < 0 or percentage > 100):
            raise forms.ValidationError("Percentage must be between 0 and 100")
        
        return cleaned_data