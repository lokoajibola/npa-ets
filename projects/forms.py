from django import forms
from django.utils import timezone
from .models import Project, ProjectStage, ProjectDocument, ProgressReport
from django.contrib.auth import get_user_model
from .models import ProjectStage, BOQItem 

User = get_user_model()

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
    

class SiteInspectionForm(forms.ModelForm):
    inspection_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    inspection_team = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))
    findings = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}))
    
    class Meta:
        model = ProjectStage
        fields = ['status', 'start_date', 'end_date', 'assigned_to', 'document', 'notes']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['document'].label = "Inspection Report"

class ProjectProposalForm(forms.ModelForm):
    proposal_number = forms.CharField(max_length=50)
    proposal_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    estimated_cost = forms.DecimalField(max_digits=15, decimal_places=2)
    
    class Meta:
        model = ProjectStage
        fields = ['status', 'start_date', 'end_date', 'assigned_to', 'document', 'notes']

class ContractAwardForm(forms.ModelForm):
    contract_amount = forms.DecimalField(max_digits=15, decimal_places=2)
    contract_duration = forms.IntegerField(help_text="Duration in days")
    performance_bond = forms.DecimalField(max_digits=15, decimal_places=2, required=False)
    
    class Meta:
        model = ProjectStage
        fields = ['status', 'start_date', 'end_date', 'contractor', 
                 'contract_reference', 'contract_date', 'contract_amount',
                 'document', 'notes']
        
from django.forms import modelformset_factory, inlineformset_factory

class BOQItemForm(forms.ModelForm):
    class Meta:
        model = BOQItem
        fields = ['section', 'item_number', 'description', 'quantity', 'unit', 'rate', 'notes']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control quantity-input', 'step': '0.01'}),
            'rate': forms.NumberInput(attrs={'class': 'form-control rate-input', 'step': '0.01'}),
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'section': forms.TextInput(attrs={'class': 'form-control'}),
            'item_number': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.TextInput(attrs={'class': 'form-control'}),
        }

# Create formset factory
BOQItemFormSet = inlineformset_factory(
    ProjectStage,
    BOQItem,
    form=BOQItemForm,
    extra=1,  # Start with 1 empty row
    can_delete=True,
    can_order=False,
)
# stages/forms.py
from django import forms
from .models import BOQBEME, ProjectStage
from accounts.models import User

class BOQBEMEForm(forms.ModelForm):
    class Meta:
        model = BOQBEME
        fields = ['document', 'notes', 'status']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['document'].label = "BEME Document (PDF)"
        self.fields['document'].required = False
        self.fields['notes'].required = False
        self.fields['status'].required = False
        
class DueDiligenceForm(forms.ModelForm):
    due_diligence_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    site_conditions = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), 
                                     label="Site Conditions Assessment")
    environmental_impact = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), 
                                         label="Environmental Impact Assessment")
    risk_assessment = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), 
                                     label="Risk Assessment")
    legal_clearance = forms.BooleanField(required=False, label="Legal Clearance Obtained")
    regulatory_compliance = forms.BooleanField(required=False, label="Regulatory Compliance")
    
    class Meta:
        model = ProjectStage
        fields = ['status', 'start_date', 'end_date', 'assigned_to', 'document', 'notes']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['document'].label = "Due Diligence Report"

class ProjectCertificationForm(forms.ModelForm):
    certificate_number = forms.CharField(max_length=50, label="Certificate Number")
    certificate_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    amount_certified = forms.DecimalField(max_digits=15, decimal_places=2, label="Amount Certified (₦)")
    work_certified = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), 
                                    label="Work Certified")
    certified_by = forms.ModelChoiceField(
        queryset=User.objects.filter(office__in=['chief_port_engineer', 'general_manager', 'executive_director']),
        label="Certified By"
    )
    
    class Meta:
        model = ProjectStage
        fields = ['status', 'start_date', 'end_date', 'document', 'notes']

class ContractAwardForm(forms.ModelForm):
    contract_amount = forms.DecimalField(max_digits=15, decimal_places=2, label="Contract Amount (₦)")
    contract_duration = forms.IntegerField(label="Contract Duration (days)")
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Contract Start Date")
    completion_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Contract Completion Date")
    performance_bond = forms.DecimalField(max_digits=15, decimal_places=2, required=False, 
                                         label="Performance Bond Amount (₦)")
    advance_payment = forms.DecimalField(max_digits=15, decimal_places=2, required=False,
                                        label="Advance Payment (₦)")
    retention_percentage = forms.IntegerField(min_value=0, max_value=100, initial=5,
                                            label="Retention Percentage (%)")
    
    class Meta:
        model = ProjectStage
        fields = ['status', 'contractor', 'contract_reference', 'contract_date', 
                 'document', 'notes']

class NominationSupervisorForm(forms.ModelForm):
    project_manager = forms.ModelChoiceField(
        queryset=User.objects.filter(office='engineer', grade_level__gte=10),
        label="Project Manager"
    )
    supervisor = forms.ModelChoiceField(
        queryset=User.objects.filter(office='engineer'),
        label="Project Supervisor"
    )
    appointment_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    terms_of_reference = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    authority_level = forms.ChoiceField(choices=[
        ('full', 'Full Authority'),
        ('limited', 'Limited Authority'),
        ('monitoring', 'Monitoring Only')
    ])
    
    class Meta:
        model = ProjectStage
        fields = ['status', 'start_date', 'end_date', 'document', 'notes']