# projects/models.py - COMPLETE AND WORKING VERSION
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from django.utils import timezone

User = get_user_model()

# Contractor Model
class Contractor(models.Model):
    contractor_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=200)
    registration_number = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    tax_id = models.CharField(max_length=50)
    classification = models.CharField(max_length=100)
    is_blacklisted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.registration_number})"

# Add this at the top with other choices
PORT_LOCATION_CHOICES = [
    ('hq', 'Headquarters (HQ)'),
    ('lpc', 'Lagos Port Complex (LPC)'),
    ('tincan', 'Tincan Island Port Complex (TCIPC)'),
    ('rivers', 'Rivers Port (RP)'),
    ('delta', 'Delta Port (DP)'),
    ('calabar', 'Calabar Port (CAL)'),
    ('lekki', 'Lekki Port'),
    ('flt', 'Federal Lighter Terminal Onne (FLT)'),
    ('fot', 'Federal Ocean Terminal (FOT)'),
    ('other', 'Other'),
]

BUDGET_TYPE_CHOICES = [
    ('capex', 'CAPEX - Capital Expenditure'),
    ('opex', 'OPEX - Operational Expenditure'),
    ('overhead', 'Overhead'),
    ('special', 'Special Project'),
]

DEPARTMENT_CHOICES = [
    ('civil', 'Civil Engineering'),
    ('electrical', 'Electrical Engineering'),
    ('mechanical', 'Mechanical Engineering'),
    ('marine', 'Marine Engineering'),
    ('planning', 'Planning & Design'),
    ('maintenance', 'Maintenance'),
    ('dredging', 'Dredging'),
    ('csr', 'Corporate Social Responsibility'),
]

# Project Model - MUST EXIST AND BE DEFINED FIRST
class Project(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low Priority'),
        ('medium', 'Medium Priority'),
        ('high', 'High Priority'),
        ('critical', 'Critical Priority'),
    ]
    
    PROJECT_TYPE_CHOICES = [
        ('civil', 'Civil Works'),
        ('electrical', 'Electrical Installation'),
        ('mechanical', 'Mechanical Works'),
        ('marine', 'Marine Works'),
        ('dredging', 'Dredging Works'),
        ('maintenance', 'Maintenance'),
        ('rehabilitation', 'Rehabilitation'),
        ('new_construction', 'New Construction'),
    ]

    
    project_id = models.CharField(max_length=50, unique=True, primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    project_type = models.CharField(max_length=50, choices=PROJECT_TYPE_CHOICES)
    location = models.CharField(max_length=50, choices=PORT_LOCATION_CHOICES, default='hq')
    other_location = models.CharField(max_length=200, blank=True, help_text="Specify if location is 'Other'")
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, default='civil')

    # Budget fields
    estimated_budget = models.DecimalField(max_digits=15, decimal_places=2)
    approved_budget = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    spent_budget = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Timeline
    proposed_start_date = models.DateField(null=True, blank=True)
    proposed_end_date = models.DateField(null=True, blank=True)
    approved_start_date = models.DateField(null=True, blank=True)
    approved_end_date = models.DateField(null=True, blank=True)
    actual_start_date = models.DateField(null=True, blank=True)
    actual_end_date = models.DateField(null=True, blank=True)
    
    # Status and priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Personnel
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_projects')
    project_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                        related_name='managed_projects')
    supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='supervised_projects')
    
    # Contractor
    contractor = models.ForeignKey(Contractor, on_delete=models.SET_NULL, null=True, blank=True)
    contractor_address = models.CharField(max_length=100, blank=True)
    contractor_phone = models.CharField(max_length=20, blank=True)

    # Contract fields
    contract_sum = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Total contract sum")
    contingencies = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0)
    contract_award_date = models.DateField(null=True, blank=True)
    contract_award_ref = models.CharField(max_length=100, blank=True)
    contract_duration = models.IntegerField(null=True, blank=True, help_text="Duration in days")
    performance_bond = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    advance_payment = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    retention_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=5.00)
    contract_completion_date = models.DateField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Approval chain
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='reviewed_projects')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='approved_projects')
    

    budget_head = models.CharField(max_length=100, blank=True, help_text="Budget head code/reference")

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.project_id} - {self.title}"
    
    def save(self, *args, **kwargs):
        # Generate project ID if not set
        if not self.project_id:
            self.project_id = self.generate_project_id()
        super().save(*args, **kwargs)
    
    def generate_project_id(self):
        year = timezone.now().year
        count = Project.objects.filter(
            project_id__startswith=f"NPA-ENG-{year}-"
        ).count() + 1
        return f"NPA-ENG-{year}-{count:03d}"
    
    @property
    def is_overdue(self):
        if self.status == 'in_progress' and self.approved_end_date:
            return timezone.now().date() > self.approved_end_date
        return False
    
    @property
    def progress_percentage(self):
        completed_stages = self.stages.filter(status='completed').count()
        total_stages = self.stages.count()
        return round((completed_stages / total_stages * 100), 1) if total_stages > 0 else 0

# Project Stage Model
class ProjectStage(models.Model):
    STAGE_CHOICES = [
        ('site_inspection', 'Site Inspection'),
        ('project_proposal', 'Project Proposal Preparation'),
        ('feasibility_study', 'Feasibility Study'),
        ('due_diligence', 'Due Diligence (Terms of Reference)'),
        ('prepare_boq', 'Prepare BOQ/BEME'),
        ('technical_review', 'Technical Review Committee'),
        ('forward_gm', 'Forward to General Manager Engineering'),
        ('forward_ed', 'Forward to Executive Director Engineering'),
        ('tender_process', 'Tender Process'),
        ('contract_award', 'Contract Award'),
        ('nominate_pm', 'Nomination of Project Manager/Supervisor'),
        ('commencement', 'Commencement of Project'),
        ('supervision', 'Supervision (Monitoring & Evaluation)'),
        ('progress_report', 'Submission of Progress Report'),
        ('payment_certificate', 'Project Certification (Payment Certificate)'),
        ('completion', 'Project Completion/Commissioning'),
        ('retention_certificate', 'Certification of Retention'),
        ('final_report', 'Final Project Report'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('blocked', 'Blocked'),
        ('requires_approval', 'Requires Approval'),
    ]
    
    stage_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='stages')  # Use string reference
    stage_type = models.CharField(max_length=50, choices=STAGE_CHOICES)
    order = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Dates
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    
    # Personnel
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                   related_name='assigned_stages')
    forward_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='forwarded_stages'
    )
    
    # Stage-specific fields
    contractor = models.ForeignKey(Contractor, on_delete=models.SET_NULL, null=True, blank=True)
    contract_reference = models.CharField(max_length=100, blank=True)
    contract_date = models.DateField(null=True, blank=True)
    
    # Documents
    document = models.FileField(upload_to='project_documents/stages/', null=True, blank=True)
    is_document_uploaded = models.BooleanField(default=False)
    
    # Approval
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='approved_stages')
    approval_date = models.DateTimeField(null=True, blank=True)
    
    # Status
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['project', 'stage_type']
    
    def __str__(self):
        return f"{self.project.project_id} - {self.get_stage_type_display()}"

# Progress Report Model
class ProgressReport(models.Model):
    report_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='progress_reports')  # Use string reference
    report_date = models.DateField()
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Progress metrics
    percentage_complete = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    work_accomplished = models.TextField()
    challenges = models.TextField(blank=True)
    next_activities = models.TextField()
    
    # Approval
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_reports')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-report_date']
    
    def __str__(self):
        return f"Progress Report - {self.project.project_id} - {self.report_date}"

# Document Model
class ProjectDocument(models.Model):
    DOCUMENT_TYPES = [
        ('proposal', 'Project Proposal'),
        ('feasibility_study', 'Feasibility Study'),
        ('tor', 'Terms of Reference'),
        ('boq', 'BOQ/BEME'),
        ('technical_spec', 'Technical Specifications'),
        ('tender_doc', 'Tender Document'),
        ('contract', 'Contract Agreement'),
        ('progress_report', 'Progress Report'),
        ('payment_cert', 'Payment Certificate'),
        ('completion_cert', 'Completion Certificate'),
        ('inspection_report', 'Inspection Report'),
        ('other', 'Other'),
    ]
    
    document_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='documents')  # Use string reference
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='project_documents/%Y/%m/%d/')
    
    # Metadata
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} - {self.project.project_id}"

class Budget(models.Model):
    BUDGET_TYPE_CHOICES = [
        ('capex', 'CAPEX - Capital Expenditure'),
        ('opex', 'OPEX - Operational Expenditure'),
        ('overhead', 'Overhead'),
        ('special', 'Special Project'),
    ]
    
    budget_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    budget_code = models.CharField(max_length=50, unique=True, help_text="e.g., ENG-CAP-2026-001")
    budget_head = models.CharField(max_length=200)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    year = models.IntegerField()
    budget_type = models.CharField(max_length=20, choices=BUDGET_TYPE_CHOICES)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-year', 'department', 'budget_code']
    
    def __str__(self):
        return f"{self.budget_code} - {self.budget_head} ({self.get_department_display()})"

class BudgetItem(models.Model):
    item_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='items', default=None, null=True, blank=True)
    
    ctr = models.CharField(max_length=50, help_text="Cost Tracking Reference")
    expenditure_description = models.TextField()
    proposed_amount = models.DecimalField(max_digits=15, decimal_places=2)
    justification = models.TextField(blank=True)
    remarks = models.TextField(blank=True)
    
    # For section grouping
    section = models.CharField(max_length=200, default='Main Budget')
    order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['section', 'order']
    
    def __str__(self):
        return f"{self.ctr} - {self.expenditure_description[:50]}"

class ProjectBudgetAllocation(models.Model):
    """Links a project to a budget head"""
    allocation_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='budget_allocations')
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='project_allocations')
    allocated_amount = models.DecimalField(max_digits=15, decimal_places=2)
    remaining_balance = models.DecimalField(max_digits=15, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['project', 'budget']
    
    def __str__(self):
        return f"{self.project.project_id} - {self.budget.budget_head}"

class ProjectNomination(models.Model):
    NOMINATION_TYPES = [
        ('project_manager', 'Project Manager'),
        ('supervisor', 'Project Supervisor'),
    ]
    
    NOMINATION_STATUS = [
        ('pending_gm', 'Pending GM Approval'),
        ('pending_ed', 'Pending ED Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    nomination_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='nominations')
    nomination_type = models.CharField(max_length=20, choices=NOMINATION_TYPES)
    
    # Nominee details
    nominee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_nominations')
    nominee_office = models.CharField(max_length=100, null=True, blank=True)  # Store office at time of nomination
    nominee_department = models.CharField(max_length=100, null=True, blank=True)  # Store department at time of nomination
    
    # Project location at time of nomination
    project_location = models.CharField(max_length=200)
    
    # Approval chain
    nominated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='nominated_projects'
    )
    nominator_office = models.CharField(max_length=100, null=True, blank=True)  # Store nominator's office
    
    gm_approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='gm_approved_nominations'
    )
    ed_approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='ed_approved_nominations'
    )
    
    # Status and dates
    status = models.CharField(max_length=20, choices=NOMINATION_STATUS, default='pending_gm')
    gm_approved_at = models.DateTimeField(null=True, blank=True)
    ed_approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Rejection reason
    rejection_reason = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        # Allow multiple nominations of same type (for multiple managers/supervisors)
        # But prevent duplicate active nominations for same person
        unique_together = ['project', 'nomination_type', 'nominee', 'status']
    
    def __str__(self):
        return f"{self.project.project_id} - {self.get_nomination_type_display()} - {self.nominee.get_full_name()}"
    
    def save(self, *args, **kwargs):
        # Store office and department at time of nomination
        if not self.nominee_office:
            self.nominee_office = self.nominee.get_office_display()
        if not self.nominee_department:
            self.nominee_department = self.nominee.get_department_display()
        if self.nominated_by and not self.nominator_office:
            self.nominator_office = self.nominated_by.get_office_display()
        super().save(*args, **kwargs)

# projects/models.py
class PaymentCertificate(models.Model):
    certificate_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='payment_certificates')
    stage = models.ForeignKey(ProjectStage, on_delete=models.CASCADE, related_name='payment_certificates')
    
    # Certificate info
    certificate_no = models.CharField(max_length=50)
    certificate_date = models.DateField()
    
    # Input fields (matching your Excel layout)
    contingencies = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    estimated_omission = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    estimated_addition = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    work_completed_to_date = models.DecimalField(max_digits=15, decimal_places=2)
    cost_of_escalation = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    materials_on_site = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    retention_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    fluctuation_claims = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    refund_advance_payment = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    amount_previously_certified = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Calculated fields (can be properties instead of stored fields)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-certificate_date']
    
    def __str__(self):
        return f"{self.certificate_no} - {self.project.project_id}"
    
    @property
    def contract_sum(self):
        return self.project.contract_sum or 0
    
    @property
    def estimated_total_cost(self):
        """ESTIMATED TOTAL COST OF WORKS"""
        return (self.contract_sum - self.contingencies - 
                self.estimated_omission + self.estimated_addition)
    
    @property
    def total_value_works(self):
        """TOTAL VALUE OF WORKS AND MATERIALS ON SITE (4)"""
        return self.cost_of_escalation + self.materials_on_site
    
    @property
    def retention_amount(self):
        """RETENTION AMOUNT (5)"""
        return self.work_completed_to_date * (self.retention_rate / 100)
    
    @property
    def total_net_payment(self):
        """TOTAL NET PAYMENT (7)"""
        return (self.work_completed_to_date + self.total_value_works - 
                self.retention_amount + self.fluctuation_claims)
    
    @property
    def total_net_amount_payable(self):
        """TOTAL NET AMOUNT PAYABLE (9)"""
        return self.total_net_payment - self.refund_advance_payment
    
    @property
    def amount_now_payable(self):
        """AMOUNT NOW PAYABLE (11)"""
        return self.total_net_amount_payable - self.amount_previously_certified
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

# Technical Review Committee Model
class TechnicalReview(models.Model):
    review_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='technical_reviews')
    review_date = models.DateField()
    committee_members = models.ManyToManyField(User, related_name='technical_committees')
    findings = models.TextField()
    recommendations = models.TextField()
    decision = models.CharField(max_length=30, choices=[
        ('approved', 'Approved'),
        ('approved_with_revisions', 'Approved with Revisions'),
        ('rejected', 'Rejected'),
        ('deferred', 'Deferred'),
    ])
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-review_date']
    
    def __str__(self):
        return f"Tech Review - {self.project.project_id} - {self.review_date}"

# projects/models.py - Update BOQItem model
class BOQItem(models.Model):
    UNIT_CHOICES = [
        ('item', 'Item'),
        ('nos', 'Nos'),
        ('sqm', 'Sqm'),
        ('m', 'M'),
        ('m2', 'M²'),
        ('m3', 'M³'),
        ('kg', 'Kg'),
        ('ton', 'Ton'),
        ('day', 'Day'),
        ('hour', 'Hour'),
        ('lot', 'Lot'),
    ]
    
    boq_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    project_stage = models.ForeignKey(ProjectStage, on_delete=models.CASCADE, related_name='boq_items')
    section = models.CharField(max_length=100, default='Main Section')
    item_number = models.CharField(max_length=20, default='1')
    description = models.TextField()
    quantity = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='item')
    rate = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'item_number']
    
    def save(self, *args, **kwargs):
        # Auto-calculate amount
        self.amount = self.quantity * self.rate
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.item_number} - {self.description[:50]}"