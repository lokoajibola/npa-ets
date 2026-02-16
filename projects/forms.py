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

# projects/forms.py
from django import forms
from .models import ProjectStage, Contractor

class ContractorForm(forms.ModelForm):
    class Meta:
        model = Contractor
        fields = [
            'name', 'registration_number', 'contact_person', 
            'phone', 'email', 'address', 'tax_id', 'classification'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MESSRS Contractor Name'}),
            'registration_number': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+234-XXX-XXX-XXXX'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tax_id': forms.TextInput(attrs={'class': 'form-control'}),
            'classification': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Contractor Name',
            'registration_number': 'Registration Number',
            'contact_person': 'Contact Person',
            'phone': 'Phone Number',
            'email': 'Email Address',
            'address': 'Address',
            'tax_id': 'Tax ID / VAT Number',
            'classification': 'Classification',
        }

class ContractAwardForm(forms.ModelForm):
    # Keep contractor as ModelChoiceField but customize the display
    contractor = forms.ModelChoiceField(
        queryset=Contractor.objects.all(),
        required=True,
        label="Contractor",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Add a display field for "MESSRS" prefix
    contractor_display = forms.CharField(
        max_length=200,
        required=False,
        label="Contractor Name",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
            'style': 'background-color: #f8f9fa;'
        })
    )
    
    contract_amount = forms.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        label="Contract Amount (₦)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    
    contract_duration = forms.IntegerField(
        help_text="Duration in days",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    performance_bond = forms.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        required=False,
        label="Performance Bond (₦)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    
    advance_payment = forms.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        required=False,
        label="Advance Payment (₦)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    
    retention_percentage = forms.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        required=False,
        label="Retention Percentage (%)",
        initial=5.00,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    
    completion_date = forms.DateField(
        required=False,
        label="Expected Completion Date",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    class Meta:
        model = ProjectStage
        fields = ['status', 'start_date', 'contract_date', 'contract_reference', 
                 'document', 'notes']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'contract_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'contract_reference': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'document': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make contractor_display show MESSRS + contractor name
        if self.instance and self.instance.contractor:
            self.fields['contractor_display'].initial = f"MESSRS {self.instance.contractor.name}"
            
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

# projects/forms.py
from django import forms
from .models import PaymentCertificate

class PaymentCertificateForm(forms.ModelForm):
    class Meta:
        model = PaymentCertificate
        fields = [
            'certificate_no', 'certificate_date',
            'contingencies', 'estimated_omission', 'estimated_addition',
            'work_completed_to_date', 'cost_of_escalation', 'materials_on_site',
            'retention_rate', 'fluctuation_claims', 'refund_advance_payment',
            'amount_previously_certified'
        ]
        widgets = {
            'certificate_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'certificate_no': forms.TextInput(attrs={'class': 'form-control'}),
            'contingencies': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estimated_omission': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estimated_addition': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'work_completed_to_date': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cost_of_escalation': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'materials_on_site': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'retention_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fluctuation_claims': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'refund_advance_payment': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'amount_previously_certified': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        labels = {
            'certificate_no': 'Payment Certificate No',
            'certificate_date': 'Date',
            'contingencies': 'LESS CONTINGENCIES',
            'estimated_omission': 'LESS ESTIMATED OMISSION',
            'estimated_addition': 'ADD ESTIMATED ADDITION',
            'work_completed_to_date': 'WORK COMPLETED TO DATE',
            'cost_of_escalation': 'COST OF ESCALATION',
            'materials_on_site': 'MATERIALS ON SITE',
            'retention_rate': 'RETENTION RATE (%)',
            'fluctuation_claims': 'FLUCTUATION/OTHER CLAIMS',
            'refund_advance_payment': 'REFUND OF ADVANCE PAYMENT',
            'amount_previously_certified': 'AMOUNT PREVIOUSLY CERTIFIED',
        }


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