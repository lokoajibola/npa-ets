from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from .models import Project, ProjectStage, ProjectDocument, ProgressReport, Contractor
from .forms import ProjectForm, ProjectStageForm, ProjectDocumentForm, ProgressReportForm
from django.utils import timezone

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
    pk_url_kwarg = 'pk'
    
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
    pk_url_kwarg = 'pk'
    
    def get_success_url(self):
        return reverse_lazy('project_detail', kwargs={'pk': self.object.pk})
    
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
        return redirect('project_detail', pk=project_id)
    
    if request.method == 'POST':
        form = ProjectStageForm(request.POST, request.FILES, instance=stage)
        if form.is_valid():
            stage = form.save()
            
            # If stage is completed, update dates
            if stage.status == 'completed' and not stage.end_date:
                stage.end_date = timezone.now().date()
                stage.save()
            
            messages.success(request, f'{stage.get_stage_type_display()} stage updated!')
            return redirect('project_detail', pk=project_id)
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