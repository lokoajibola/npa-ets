from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from .models import PaymentCertificate, Project, ProjectStage, ProjectDocument, ProgressReport, Contractor, BOQItem
from .forms import ProjectForm, ProjectStageForm, ProjectDocumentForm, ProgressReportForm, SiteInspectionForm, ProjectProposalForm, ContractAwardForm, DueDiligenceForm, PaymentCertificateForm, NominationSupervisorForm
from django.utils import timezone
from .forms import ContractorForm

@login_required
def contractor_list(request):
    contractors = Contractor.objects.all().order_by('name')
    return render(request, 'contractors/contractor_list.html', {
        'contractors': contractors,
        'page_title': 'Contractors'
    })

@login_required
def contractor_create(request):
    if request.method == 'POST':
        form = ContractorForm(request.POST)
        if form.is_valid():
            contractor = form.save()
            messages.success(request, f'Contractor "{contractor.name}" created successfully!')
            
            # If coming from a project, redirect back to that project
            project_id = request.GET.get('project')
            stage_id = request.GET.get('stage')
            if project_id and stage_id:
                return redirect('contract_award', project_id=project_id, stage_id=stage_id)
            return redirect('contractor_list')
    else:
        form = ContractorForm(initial={'name': 'MESSRS '})
    
    return render(request, 'contractors/contractor_form.html', {
        'form': form,
        'page_title': 'Add Contractor'
    })

@login_required
def contractor_update(request, contractor_id):
    contractor = get_object_or_404(Contractor, contractor_id=contractor_id)
    
    if request.method == 'POST':
        form = ContractorForm(request.POST, instance=contractor)
        if form.is_valid():
            form.save()
            messages.success(request, f'Contractor "{contractor.name}" updated successfully!')
            return redirect('contractor_list')
    else:
        form = ContractorForm(instance=contractor)
    
    return render(request, 'contractors/contractor_form.html', {
        'form': form,
        'contractor': contractor,
        'page_title': f'Edit {contractor.name}'
    })

@login_required
def contractor_detail(request, contractor_id):
    contractor = get_object_or_404(Contractor, contractor_id=contractor_id)
    projects = Project.objects.filter(contractor=contractor)
    
    return render(request, 'contractors/contractor_detail.html', {
        'contractor': contractor,
        'projects': projects,
        'page_title': contractor.name
    })

# Project List View
class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 10
    
    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        # Filter based on user role
        if user.office == 'executive_director':
            pass  # Show all projects
        elif user.office == 'general_manager':
            queryset = queryset.filter(
                Q(status__in=['submitted', 'under_review', 'approved', 'in_progress']) |
                Q(created_by=user)
            )
        elif user.office in ['assistant_general_manager', 'chief_port_engineer', 'unit_head']:
            queryset = queryset.filter(
                Q(created_by__department=user.department) |
                Q(created_by=user) |
                Q(project_manager=user) |
                Q(supervisor=user)
            )
        else:  # Engineers
            queryset = queryset.filter(
                Q(created_by=user) |
                Q(project_manager=user) |
                Q(supervisor=user) |
                Q(stages__assigned_to=user)
            ).distinct()
        
        # Apply filters from GET parameters
        status = self.request.GET.get('status')
        project_type = self.request.GET.get('project_type')
        priority = self.request.GET.get('priority')
        
        if status:
            queryset = queryset.filter(status=status)
        if project_type:
            queryset = queryset.filter(project_type=project_type)
        if priority:
            queryset = queryset.filter(priority=priority)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Project.STATUS_CHOICES
        context['project_type_choices'] = Project.PROJECT_TYPE_CHOICES
        context['priority_choices'] = Project.PRIORITY_CHOICES
        context['page_title'] = 'Projects Management'
        return context

# Project Detail View
class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'
    
    pk_url_kwarg = 'project_id'  # ADD THIS LINE
    slug_field = 'project_id'    # ADD THIS LINE
    slug_url_kwarg = 'project_id'  # ADD THIS LINE
    
    def get_object(self):
        # Look up by project_id instead of pk
        project_id = self.kwargs.get('project_id') or self.kwargs.get('pk')
        return get_object_or_404(Project, project_id=project_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        
        # Get all stages
        stages = project.stages.all().order_by('order')
        
        # Arrange in 4x4 grid
        grid = []
        for i in range(0, len(stages), 4):
            grid.append(stages[i:i+4])
        
        # Get recent documents
        documents = project.documents.all().order_by('-uploaded_at')[:5]
        
        # Get progress reports
        progress_reports = project.progress_reports.all().order_by('-report_date')[:3]
        
        context.update({
            'stages_grid': grid,
            'documents': documents,
            'progress_reports': progress_reports,
            'page_title': f'Project: {project.title}',
        })
        return context

# Project Create View
class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    success_url = reverse_lazy('project_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        # Create default project stages
        self.create_project_stages(self.object)
        
        messages.success(self.request, 'Project created successfully!')
        return response
    
    def create_project_stages(self, project):
        stages_data = [
            ('site_inspection', 1),
            ('project_proposal', 2),
            ('feasibility_study', 3),
            ('due_diligence', 4),
            ('prepare_boq', 5),
            ('technical_review', 6),
            ('forward_gm', 7),
            ('forward_ed', 8),
            ('tender_process', 9),
            ('contract_award', 10),
            ('nominate_pm', 11),
            ('commencement', 12),
            ('supervision', 13),
            ('progress_report', 14),
            ('payment_certificate', 15),
            ('completion', 16),
            ('retention_certificate', 17),
            ('final_report', 18),
        ]
        
        for stage_type, order in stages_data:
            ProjectStage.objects.create(
                project=project,
                stage_type=stage_type,
                order=order
            )

# Project Update View
class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    # pk_url_kwarg = 'pk'

    def get_object(self):
        # Get project by project_id instead of pk
        project_id = self.kwargs.get('project_id')
        return get_object_or_404(Project, project_id=project_id)
    
    def get_success_url(self):
        return reverse_lazy('project_detail', kwargs={'project_id': self.object.project_id})
    
    # def get_success_url(self):
    #     return reverse_lazy('project_detail', kwargs={'pk': self.object.pk})
    
    def dispatch(self, request, *args, **kwargs):
        project = self.get_object()
        # Only creator or admin can edit
        if not (request.user == project.created_by or request.user.is_superuser):
            messages.error(request, "You don't have permission to edit this project.")
            return redirect('project_detail', pk=project.pk)
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, 'Project updated successfully!')
        return super().form_valid(form)

# Update Project Stage
@login_required
def update_stage(request, project_id, stage_id):
    project = get_object_or_404(Project, project_id=project_id)
    stage = get_object_or_404(ProjectStage, stage_id=stage_id, project=project)
    
    # Check permission
    if not (request.user == stage.assigned_to or 
            request.user == project.created_by or 
            request.user.office in ['executive_director', 'general_manager']):
        messages.error(request, "You don't have permission to update this stage.")
        return redirect('project_detail', project_id=project_id)  # Changed from pk= to project_id=
    
    if request.method == 'POST':
        form = ProjectStageForm(request.POST, request.FILES, instance=stage)
        if form.is_valid():
            stage = form.save()
            
            # If stage is completed, update dates
            if stage.status == 'completed' and not stage.end_date:
                stage.end_date = timezone.now().date()
                stage.save()
            
            messages.success(request, f'{stage.get_stage_type_display()} stage updated!')
            return redirect('project_detail', project_id=project_id)  # Changed from pk= to project_id=
    else:
        form = ProjectStageForm(instance=stage)
    
    context = {
        'form': form,
        'project': project,
        'stage': stage,
        'page_title': f'Update {stage.get_stage_type_display()}',
    }
    return render(request, 'projects/stage_form.html', context)

# Project Documents
@login_required
def project_documents(request, project_id):
    project = get_object_or_404(Project, project_id=project_id)
    documents = project.documents.all()
    
    context = {
        'project': project,
        'documents': documents,
        'page_title': f'Documents - {project.title}',
    }
    return render(request, 'projects/documents.html', context)

@login_required
def upload_document(request, project_id):
    project = get_object_or_404(Project, project_id=project_id)
    
    if request.method == 'POST':
        form = ProjectDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.project = project
            document.uploaded_by = request.user
            document.save()
            messages.success(request, 'Document uploaded successfully!')
            return redirect('project_documents', project_id=project_id)
    else:
        form = ProjectDocumentForm()
    
    context = {
        'form': form,
        'project': project,
        'page_title': 'Upload Document',
    }
    return render(request, 'projects/document_form.html', context)

# Progress Reports
@login_required
def progress_reports(request, project_id):
    project = get_object_or_404(Project, project_id=project_id)
    reports = project.progress_reports.all()
    
    context = {
        'project': project,
        'reports': reports,
        'page_title': f'Progress Reports - {project.title}',
    }
    return render(request, 'projects/progress_reports.html', context)

@login_required
def create_progress_report(request, project_id):
    project = get_object_or_404(Project, project_id=project_id)
    
    if request.method == 'POST':
        form = ProgressReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.project = project
            report.submitted_by = request.user
            report.save()
            messages.success(request, 'Progress report submitted!')
            return redirect('progress_reports', project_id=project_id)
    else:
        form = ProgressReportForm()
    
    context = {
        'form': form,
        'project': project,
        'page_title': 'Create Progress Report',
    }
    return render(request, 'projects/progress_report_form.html', context)

# Quick Actions
@login_required
def submit_project(request, project_id):
    project = get_object_or_404(Project, project_id=project_id)
    
    if request.user != project.created_by:
        messages.error(request, "Only the project creator can submit for approval.")
        return redirect('project_detail', pk=project_id)
    
    project.status = 'submitted'
    project.submitted_at = timezone.now()
    project.save()
    
    messages.success(request, 'Project submitted for approval!')
    return redirect('project_detail', pk=project_id)

@login_required
def approve_project(request, project_id):
    project = get_object_or_404(Project, project_id=project_id)
    
    # Only management can approve
    if not request.user.office in ['executive_director', 'general_manager']:
        messages.error(request, "Only management can approve projects.")
        return redirect('project_detail', pk=project_id)
    
    project.status = 'approved'
    project.approved_by = request.user
    project.approved_at = timezone.now()
    project.save()
    
    messages.success(request, 'Project approved!')
    return redirect('project_detail', pk=project_id)

@login_required
def complete_project(request, project_id):
    project = get_object_or_404(Project, project_id=project_id)
    
    # Only project manager or management can complete
    if not (request.user == project.project_manager or 
            request.user.office in ['executive_director', 'general_manager']):
        messages.error(request, "Only project manager or management can complete projects.")
        return redirect('project_detail', pk=project_id)
    
    project.status = 'completed'
    project.actual_end_date = timezone.now().date()
    project.save()
    
    messages.success(request, 'Project marked as completed!')
    return redirect('project_detail', pk=project_id)

@login_required
def site_inspection_view(request, project_id, stage_id):
    return stage_specific_view(request, project_id, stage_id, 
                              'site_inspection', SiteInspectionForm,
                              'stages/site_inspection.html')

@login_required
def project_proposal_view(request, project_id, stage_id):
    return stage_specific_view(request, project_id, stage_id,
                              'project_proposal', ProjectProposalForm,
                              'stages/project_proposal.html')

@login_required
def contract_award_view(request, project_id, stage_id):
    project = get_object_or_404(Project, project_id=project_id)
    stage = get_object_or_404(ProjectStage, stage_id=stage_id, project=project)
    
    if stage.stage_type != 'contract_award':
        messages.error(request, "This is not a contract award stage")
        return redirect('project_detail', project_id=project_id)
    
    if request.method == 'POST':
        form = ContractAwardForm(request.POST, request.FILES, instance=stage)
        
        if form.is_valid():
            # Save the stage
            stage = form.save(commit=False)
            
            # Get the selected contractor
            contractor = form.cleaned_data.get('contractor')
            if contractor:
                stage.contractor = contractor
                project.contractor = contractor
            
            # Save stage
            stage.save()
            
            # CRITICAL: Update project with ALL contract information
            # These fields need to exist in your Project model
            project.contract_sum = form.cleaned_data.get('contract_amount')
            project.contract_award_date = form.cleaned_data.get('contract_date')
            project.contract_award_ref = form.cleaned_data.get('contract_reference')
            project.contract_duration = form.cleaned_data.get('contract_duration')
            project.performance_bond = form.cleaned_data.get('performance_bond', 0)
            project.advance_payment = form.cleaned_data.get('advance_payment', 0)
            project.retention_percentage = form.cleaned_data.get('retention_percentage', 5.00)
            
            # Calculate completion date
            if stage.start_date and form.cleaned_data.get('contract_duration'):
                from datetime import timedelta
                project.contract_completion_date = stage.start_date + timedelta(
                    days=form.cleaned_data.get('contract_duration')
                )
            
            # Save project
            project.save()
            
            # Update stage dates if completed
            if stage.status == 'completed' and not stage.end_date:
                stage.end_date = timezone.now().date()
                stage.save()
            
            messages.success(request, 'Contract awarded successfully!')
            return redirect('project_detail', project_id=project_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-fill form with existing project data
        initial = {}
        if project.contract_sum:
            initial['contract_amount'] = project.contract_sum
        if project.contract_award_ref:
            initial['contract_reference'] = project.contract_award_ref
        if project.contract_award_date:
            initial['contract_date'] = project.contract_award_date
        if project.contract_duration:
            initial['contract_duration'] = project.contract_duration
        if project.performance_bond:
            initial['performance_bond'] = project.performance_bond
        if project.advance_payment:
            initial['advance_payment'] = project.advance_payment
        if project.retention_percentage:
            initial['retention_percentage'] = project.retention_percentage
        
        form = ContractAwardForm(instance=stage, initial=initial)
    
    context = {
        'form': form,
        'project': project,
        'stage': stage,
        'page_title': 'Contract Award',
    }
    return render(request, 'stages/contract_award.html', context)

# Stage-specific view functions
from django.http import HttpResponse, FileResponse
import json
import os
from .pdf_utils import generate_boq_pdf

from .forms import BOQItemFormSet
from decimal import Decimal
import json
from django.core.serializers.json import DjangoJSONEncoder

@login_required
def boq_beme_view(request, project_id, stage_id):
    project = get_object_or_404(Project, project_id=project_id)
    stage = get_object_or_404(ProjectStage, stage_id=stage_id, project=project)
    
    if stage.stage_type != 'prepare_boq':
        messages.error(request, "This is not a BOQ/BEME preparation stage")
        return redirect('project_detail', project_id=project_id)
    
    # Get all active users for forwarding
    from accounts.models import User
    import json
    from django.core.serializers.json import DjangoJSONEncoder
    from decimal import Decimal
    from django.utils import timezone
    
    # Get existing BOQ items for this stage
    existing_items = stage.boq_items.all().order_by('order', 'item_number')
    
    if request.method == 'POST':
        # Handle the form submission
        stage.notes = request.POST.get('notes', stage.notes)
        
        # Handle document upload
        if 'document' in request.FILES:
            stage.document = request.FILES['document']
            stage.is_document_uploaded = True
        
        stage.save()
        
        # Get BEME data from the hidden field
        beme_data = request.POST.get('beme_data', '[]')
        
        try:
            beme_items = json.loads(beme_data)
            
            # Delete existing BOQ items for this stage
            stage.boq_items.all().delete()
            
            # Create new BOQ items
            order = 0
            for item_data in beme_items:
                # Convert string values to Decimal
                quantity = Decimal(str(item_data.get('quantity', '0'))) if item_data.get('quantity') else Decimal('0')
                rate = Decimal(str(item_data.get('rate', '0'))) if item_data.get('rate') else Decimal('0')
                amount = quantity * rate
                
                BOQItem.objects.create(
                    project_stage=stage,
                    section=item_data.get('section', 'Main Section'),
                    item_number=item_data.get('sn', str(order + 1)),
                    description=item_data.get('description', ''),
                    quantity=quantity,
                    unit=item_data.get('unit', 'item'),
                    rate=rate,
                    amount=amount,
                    order=order
                )
                order += 1
            
            messages.success(request, 'BEME saved successfully!')
            
            # Check if this is a PDF generation request
            if 'generate_pdf' in request.POST:
                return redirect('beme_pdf', project_id=project.project_id, stage_id=stage.stage_id)
            
            return redirect('project_detail', project_id=project_id)
                
        except json.JSONDecodeError as e:
            messages.error(request, f'Error processing BEME data: {e}')
        except Exception as e:
            messages.error(request, f'Error saving BEME: {str(e)}')
        
        return redirect('project_detail', project_id=project_id)
    
    # Generate BEME sequence number
    beme_count = stage.boq_items.count()
    beme_sequence = f"{beme_count + 1:03d}"
    
    # Prepare initial data for the template
    initial_items = []
    sections = set()
    
    for item in existing_items:
        sections.add(item.section)
        initial_items.append({
            'sn': item.item_number,
            'section': item.section,
            'description': item.description,
            'quantity': str(item.quantity),
            'unit': item.unit,
            'rate': str(item.rate),
            'amount': str(item.amount)
        })
    
    context = {
        'form': None,
        'project': project,
        'stage': stage,
        'page_title': 'BEME Preparation',
        'beme_sequence': beme_sequence,
        'initial_items': json.dumps(initial_items),
        'existing_sections': json.dumps(list(sections)),
    }
    return render(request, 'stages/boq_beme_simple.html', context)

# projects/views.py
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from decimal import Decimal
import json

@login_required
def generate_beme_pdf(request, project_id, stage_id):
    project = get_object_or_404(Project, project_id=project_id)
    stage = get_object_or_404(ProjectStage, stage_id=stage_id, project=project)
    
    # Get BOQ items
    boq_items = stage.boq_items.all().order_by('order', 'item_number')
    
    # Group items by section and calculate section totals
    sections = {}
    section_totals = {}
    
    for item in boq_items:
        if item.section not in sections:
            sections[item.section] = []
            section_totals[item.section] = Decimal('0')
        sections[item.section].append(item)
        section_totals[item.section] += item.amount
    
    # Calculate overall totals
    subtotal = sum(item.amount for item in boq_items)
    contingency = subtotal * Decimal('0.05')
    vat = subtotal * Decimal('0.075')
    grand_total = subtotal + contingency + vat
    
    # Convert number to words
    def number_to_words(num):
        num = int(round(num))
        ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine',
                'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 
                'Seventeen', 'Eighteen', 'Nineteen']
        tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
        
        if num == 0:
            return 'Zero Naira Only'
        
        def convert_less_than_thousand(n):
            if n == 0:
                return ''
            elif n < 20:
                return ones[n]
            elif n < 100:
                return tens[n // 10] + (' ' + ones[n % 10] if n % 10 != 0 else '')
            else:
                return ones[n // 100] + ' Hundred ' + convert_less_than_thousand(n % 100)
        
        result = ''
        if num >= 1000000000:
            result += convert_less_than_thousand(num // 1000000000) + ' Billion '
            num %= 1000000000
        if num >= 1000000:
            result += convert_less_than_thousand(num // 1000000) + ' Million '
            num %= 1000000
        if num >= 1000:
            result += convert_less_than_thousand(num // 1000) + ' Thousand '
            num %= 1000
        if num > 0:
            result += convert_less_than_thousand(num)
        
        return result.strip() + ' Naira Only'
    
    context = {
        'project': project,
        'stage': stage,
        'sections': sections,
        'section_totals': section_totals,
        'subtotal': subtotal,
        'contingency': contingency,
        'vat': vat,
        'grand_total': grand_total,
        'grand_total_words': number_to_words(grand_total),
        'prepared_by': request.user,
        'beme_number': f"BEME/{project.project_id}/{timezone.now().year}/{boq_items.count() + 1:03d}",
        'generated_date': timezone.now(),
    }
    
    return render(request, 'stages/beme_pdf_print.html', context)

@login_required
def due_diligence_view(request, project_id, stage_id):
    return stage_specific_view(request, project_id, stage_id,
                              'due_diligence', DueDiligenceForm,
                              'stages/due_diligence.html')

# Convert number to words
def number_to_words(num):
        num = int(round(num))
        ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine',
                'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 
                'Seventeen', 'Eighteen', 'Nineteen']
        tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
        
        if num == 0:
            return 'Zero Naira Only'
        
        def convert_less_than_thousand(n):
            if n == 0:
                return ''
            elif n < 20:
                return ones[n]
            elif n < 100:
                return tens[n // 10] + (' ' + ones[n % 10] if n % 10 != 0 else '')
            else:
                return ones[n // 100] + ' Hundred ' + convert_less_than_thousand(n % 100)
        
        result = ''
        if num >= 1000000000:
            result += convert_less_than_thousand(num // 1000000000) + ' Billion '
            num %= 1000000000
        if num >= 1000000:
            result += convert_less_than_thousand(num // 1000000) + ' Million '
            num %= 1000000
        if num >= 1000:
            result += convert_less_than_thousand(num // 1000) + ' Thousand '
            num %= 1000
        if num > 0:
            result += convert_less_than_thousand(num)
        
        return result.strip() + ' Naira Only'
    

# projects/views.py
@login_required
def project_certification_view(request, project_id, stage_id):
    project = get_object_or_404(Project, project_id=project_id)
    stage = get_object_or_404(ProjectStage, stage_id=stage_id, project=project)
    
    if stage.stage_type != 'payment_certificate':
        messages.error(request, "This is not a payment certification stage")
        return redirect('project_detail', project_id=project_id)
    
    # Get or create payment certificate for this stage
    from .models import PaymentCertificate
    certificate, created = PaymentCertificate.objects.get_or_create(
        stage=stage,
        project=project,
        defaults={
            'certificate_no': f"CERT/{project.project_id}/{timezone.now().year}/001",
            'certificate_date': timezone.now().date(),
            'work_completed_to_date': project.contract_sum or 0,
            
        }
    )
    
    if request.method == 'POST':
        form = PaymentCertificateForm(request.POST, instance=certificate)
        
        # Handle stage completion
        stage.status = request.POST.get('stage_status', stage.status)
        stage.notes = request.POST.get('notes', stage.notes)
        
        if 'document' in request.FILES:
            stage.document = request.FILES['document']
            stage.is_document_uploaded = True
        
        stage.save()
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Payment certificate saved successfully!')
            
            if 'generate_pdf' in request.POST:
                return redirect('certificate_pdf', project_id=project.project_id, 
                              certificate_id=certificate.certificate_id)
            
            return redirect('project_detail', project_id=project_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PaymentCertificateForm(instance=certificate)
    
    context = {
        'form': form,
        'project': project,
        'stage': stage,
        'certificate': certificate,
        'page_title': 'Payment Certificate',
        
    }
    return render(request, 'stages/payment_certificate.html', context)

@login_required
def certificate_pdf_view(request, project_id, certificate_id):
    project = get_object_or_404(Project, project_id=project_id)
    certificate = get_object_or_404(PaymentCertificate, certificate_id=certificate_id, project=project)
    grand_total = certificate.amount_now_payable if certificate else 0
    context = {
        'project': project,
        'certificate': certificate,
        'generated_date': timezone.now(),
        'grand_total_words': number_to_words(grand_total),
    }
    return render(request, 'stages/certificate_pdf_print.html', context)

@login_required
def contract_award_view(request, project_id, stage_id):
    project = get_object_or_404(Project, project_id=project_id)
    stage = get_object_or_404(ProjectStage, stage_id=stage_id, project=project)
    
    if stage.stage_type != 'contract_award':
        messages.error(request, "This is not a contract award stage")
        return redirect('project_detail', project_id=project_id)
    
    if request.method == 'POST':
        form = ContractAwardForm(request.POST, request.FILES, instance=stage)
        
        if form.is_valid():
            # Save the stage first
            stage = form.save(commit=False)
            
            # Get contractor from form (if selected)
            contractor = form.cleaned_data.get('contractor')
            
            # If no contractor selected but we have contractor_name field
            if not contractor and 'contractor_name' in form.cleaned_data:
                contractor_name = form.cleaned_data.get('contractor_name', '').strip()
                if contractor_name:
                    # Clean the name (remove MESSRS prefix if present)
                    clean_name = contractor_name.replace('MESSRS', '').strip()
                    
                    # Create new contractor
                    contractor = Contractor.objects.create(
                        name=clean_name,
                        registration_number=f"CONT/{timezone.now().year}/001",
                        contact_person=clean_name,
                        phone=form.cleaned_data.get('contractor_phone', ''),
                        email=form.cleaned_data.get('contractor_email', ''),
                        address=form.cleaned_data.get('contractor_address', ''),
                        tax_id='N/A',
                        classification='General Contractor'
                    )
                    messages.info(request, f'New contractor "{clean_name}" created.')
            
            # Link contractor to stage and project
            if contractor:
                stage.contractor = contractor
                project.contractor = contractor
            
            # Save stage
            stage.save()
            
            # CRITICAL: Update project with ALL contract information
            project.contract_sum = form.cleaned_data.get('contract_amount')
            project.contract_award_date = form.cleaned_data.get('contract_date')
            project.contract_award_ref = form.cleaned_data.get('contract_reference')
            project.contract_duration = form.cleaned_data.get('contract_duration')
            project.performance_bond = form.cleaned_data.get('performance_bond', 0)
            project.advance_payment = form.cleaned_data.get('advance_payment', 0)
            project.retention_percentage = form.cleaned_data.get('retention_percentage', 5.00)
            
            # Calculate completion date
            if stage.start_date and form.cleaned_data.get('contract_duration'):
                from datetime import timedelta
                project.contract_completion_date = stage.start_date + timedelta(
                    days=form.cleaned_data.get('contract_duration')
                )
            
            # Save project with all updates
            project.save()
            
            # Update stage end date if completed
            if stage.status == 'completed' and not stage.end_date:
                stage.end_date = timezone.now().date()
                stage.save()
            
            messages.success(request, 'Contract awarded successfully! All project contract information updated.')
            return redirect('project_detail', project_id=project_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-fill form with existing project data
        initial = {}
        if project.contract_sum:
            initial['contract_amount'] = project.contract_sum
        if project.contract_award_ref:
            initial['contract_reference'] = project.contract_award_ref
        if project.contract_award_date:
            initial['contract_date'] = project.contract_award_date
        if project.contract_duration:
            initial['contract_duration'] = project.contract_duration
        if project.performance_bond:
            initial['performance_bond'] = project.performance_bond
        if project.advance_payment:
            initial['advance_payment'] = project.advance_payment
        if project.retention_percentage:
            initial['retention_percentage'] = project.retention_percentage
        
        form = ContractAwardForm(instance=stage, initial=initial)
    
    # Get all contractors for the dropdown
    contractors = Contractor.objects.all().order_by('name')
    
    context = {
        'form': form,
        'project': project,
        'stage': stage,
        'contractors': contractors,
        'page_title': 'Contract Award',
    }
    return render(request, 'stages/contract_award.html', context)

@login_required
def nomination_supervisor_view(request, project_id, stage_id):
    return stage_specific_view(request, project_id, stage_id,
                              'nominate_pm', NominationSupervisorForm,
                              'stages/nomination_supervisor.html')

# Add to views.py
@login_required
def add_contractor(request, project_id):
    project = get_object_or_404(Project, project_id=project_id)
    
    if request.method == 'POST':
        form = ContractorForm(request.POST)
        if form.is_valid():
            contractor = form.save()
            # Link to project
            project.contractor = contractor
            project.save()
            messages.success(request, f'Contractor "{contractor.name}" added and linked to project.')
            return redirect('contract_award', project_id=project_id, stage_id=stage_id)
    else:
        form = ContractorForm(initial={'name': 'MESSRS '})
    
    return render(request, 'contractors/contractor_form.html', {'form': form, 'project': project})

# Generic stage view handler
def stage_specific_view(request, project_id, stage_id, stage_type, form_class, template_name):
    project = get_object_or_404(Project, project_id=project_id)
    stage = get_object_or_404(ProjectStage, stage_id=stage_id, project=project)
    
    # Verify stage type
    if stage.stage_type != stage_type:
        messages.error(request, f"Incorrect stage type. Expected: {stage_type}")
        return redirect('project_detail', project_id=project_id)
    
    # Permission check
    user = request.user
    if not (user == stage.assigned_to or 
            user == project.created_by or 
            user.office in ['executive_director', 'general_manager', 'assistant_general_manager']):
        messages.error(request, "You don't have permission to update this stage.")
        return redirect('project_detail', project_id=project_id)
    
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=stage)
        if form.is_valid():
            stage = form.save()
            
            # Additional logic for specific stages
            if stage_type == 'contract_award' and stage.status == 'completed':
                # Update project with contractor info
                project.contractor = stage.contractor
                project.save()
                
            elif stage_type == 'nominate_pm' and stage.status == 'completed':
                # Update project with nominated personnel
                project.project_manager = form.cleaned_data.get('project_manager')
                project.supervisor = form.cleaned_data.get('supervisor')
                project.save()
            
            messages.success(request, f'{stage.get_stage_type_display()} updated successfully!')
            return redirect('project_detail', project_id=project_id)
    else:
        form = form_class(instance=stage)
    
    context = {
        'form': form,
        'project': project,
        'stage': stage,
        'page_title': stage.get_stage_type_display(),
    }
    return render(request, template_name, context)