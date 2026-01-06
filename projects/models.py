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
    location = models.CharField(max_length=200)
    port_location = models.CharField(max_length=100, blank=True)
    
    # Budget fields
    estimated_budget = models.DecimalField(max_digits=15, decimal_places=2)
    approved_budget = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    spent_budget = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Timeline
    proposed_start_date = models.DateField()
    proposed_end_date = models.DateField()
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
        """Generate NPA standard project ID: NPA/ENG/2024/001"""
        year = timezone.now().year
        count = Project.objects.filter(
            project_id__startswith=f"NPA/ENG/{year}/"
        ).count() + 1
        return f"NPA/ENG/{year}/{count:03d}"
    
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
