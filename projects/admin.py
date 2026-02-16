from django.contrib import admin
from .models import Project, Contractor, ProjectStage, ProgressReport, ProjectDocument, TechnicalReview, BOQItem, PaymentCertificate

@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    list_display = ['name', 'registration_number', 'contact_person', 'phone', 'email', 'is_blacklisted']
    list_filter = ['is_blacklisted', 'classification']
    search_fields = ['name', 'registration_number', 'contact_person']
    readonly_fields = ['contractor_id', 'created_at']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['project_id', 'title', 'project_type', 'status', 'priority', 'created_by', 'contractor']
    list_filter = ['status', 'priority', 'project_type', 'other_location']
    search_fields = ['project_id', 'title', 'description']
    readonly_fields = ['project_id', 'created_at', 'updated_at']
    raw_id_fields = ['created_by', 'project_manager', 'supervisor', 'contractor', 'reviewed_by', 'approved_by']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('project_id', 'title', 'description', 'project_type', 'location', 'other_location')
        }),
        ('Budget', {
            'fields': ('estimated_budget', 'approved_budget', 'spent_budget')
        }),
        ('Timeline', {
            'fields': ('proposed_start_date', 'proposed_end_date', 'approved_start_date', 
                      'approved_end_date', 'actual_start_date', 'actual_end_date')
        }),
        ('Status', {
            'fields': ('status', 'priority')
        }),
        ('Personnel', {
            'fields': ('created_by', 'project_manager', 'supervisor')
        }),
        ('Contractor', {
            'fields': ('contractor',)
        }),
        ('Contract Information', {
            'fields': ('contract_sum', 'contract_award_date', 'contract_award_ref', 
                      'contract_duration', 'performance_bond', 'advance_payment', 
                      'retention_percentage', 'contract_completion_date')
        }),
        ('Approval', {
            'fields': ('reviewed_by', 'approved_by', 'submitted_at', 'approved_at')
        }),
    )

@admin.register(ProjectStage)
class ProjectStageAdmin(admin.ModelAdmin):
    list_display = ['project', 'stage_type', 'order', 'status', 'assigned_to', 'due_date']
    list_filter = ['status', 'stage_type']
    search_fields = ['project__project_id', 'project__title', 'notes']
    readonly_fields = ['stage_id', 'created_at', 'updated_at']
    raw_id_fields = ['project', 'assigned_to', 'contractor', 'approved_by']

@admin.register(ProgressReport)
class ProgressReportAdmin(admin.ModelAdmin):
    list_display = ['project', 'report_date', 'period_start', 'period_end', 'percentage_complete']
    list_filter = ['report_date']
    search_fields = ['project__project_id', 'project__title']
    readonly_fields = ['report_id', 'created_at']

@admin.register(ProjectDocument)
class ProjectDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'document_type', 'uploaded_by', 'uploaded_at']
    list_filter = ['document_type', 'uploaded_at']
    search_fields = ['title', 'project__project_id', 'description']
    readonly_fields = ['document_id', 'uploaded_at']

@admin.register(TechnicalReview)
class TechnicalReviewAdmin(admin.ModelAdmin):
    list_display = ['project', 'review_date', 'decision', 'reviewed_by']
    list_filter = ['decision', 'review_date']
    search_fields = ['project__project_id', 'findings']
    readonly_fields = ['review_id', 'created_at']
    filter_horizontal = ['committee_members']

@admin.register(BOQItem)
class BOQItemAdmin(admin.ModelAdmin):
    list_display = ['project_stage', 'section', 'item_number', 'description', 'quantity', 'unit', 'rate', 'amount']
    list_filter = ['section', 'unit']
    search_fields = ['description', 'project_stage__project__project_id']
    readonly_fields = ['boq_id']

@admin.register(PaymentCertificate)
class PaymentCertificateAdmin(admin.ModelAdmin):
    list_display = ['certificate_no', 'project', 'certificate_date', 'amount_now_payable']
    list_filter = ['certificate_date']
    search_fields = ['certificate_no', 'project__project_id']
    readonly_fields = ['certificate_id', 'created_at', 'updated_at']