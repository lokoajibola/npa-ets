from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from datetime import datetime
import json

User = get_user_model()

@login_required
def dashboard(request):
    user = request.user
    
    # Import Project model here to avoid circular imports
    from projects.models import Project
    
    # Get user-specific projects
    if user.office == 'executive_director':
        projects = Project.objects.all()
    elif user.office == 'general_manager':
        projects = Project.objects.filter(
            status__in=['submitted', 'under_review', 'approved']
        )
    elif user.office in ['assistant_general_manager', 'chief_port_engineer', 'unit_head']:
        projects = Project.objects.filter(
            created_by__department=user.department
        )
    else:  # Engineers
        projects = Project.objects.filter(
            created_by=user
        )
    
    # Statistics
    total_projects = projects.count()
    active_projects = projects.filter(status='in_progress').count()
    
    # Calculate overdue projects
    overdue_projects = 0
    for project in projects.filter(status='in_progress'):
        if project.approved_end_date and project.approved_end_date < datetime.now().date():
            overdue_projects += 1
    
    # Projects requiring attention
    if user.office in ['executive_director', 'general_manager']:
        pending_approvals = Project.objects.filter(status='submitted').count()
    else:
        pending_approvals = 0
    
    # Recent projects
    recent_projects = list(projects.order_by('-created_at')[:5])
    
    # Budget statistics (simplified)
    total_budget = sum([p.estimated_budget for p in projects])
    spent_budget = sum([p.spent_budget for p in projects])
    
    context = {
        'user': user,
        'total_projects': total_projects,
        'active_projects': active_projects,
        'overdue_projects': overdue_projects,
        'pending_approvals': pending_approvals,
        'recent_projects': [],
        'total_budget': total_budget,
        'spent_budget': spent_budget,
        'page_title': 'Dashboard',
    }
    
    return render(request, 'dashboard/index.html', context)

@login_required
def analytics_view(request):
    # Only management can view analytics
    if not request.user.office in ['executive_director', 'general_manager', 'assistant_general_manager']:
        return redirect('dashboard')
    
    # Import Project model here
    from projects.models import Project
    
    # Get all projects for analytics
    projects = Project.objects.all()
    
    # Status distribution
    status_counts = {}
    for project in projects:
        status = project.get_status_display()
        status_counts[status] = status_counts.get(status, 0) + 1
    
    context = {
        'status_counts': json.dumps(status_counts),
        'total_projects': projects.count(),
        'page_title': 'Analytics',
    }
    
    return render(request, 'dashboard/analytics.html', context)