from projects.models import Project
from django.db.models import Count

from django.utils import timezone


def project_context(request):
    context = {}
    
    if request.user.is_authenticated:
        # Get user-specific stats
        if request.user.is_approving_officer:
            pending_approvals = Project.objects.filter(
                status='submitted'
            ).count()
        else:
            pending_approvals = 0
        
        context.update({
            'total_projects': Project.objects.filter(
                created_by=request.user
            ).count(),
            'active_projects': Project.objects.filter(
                created_by=request.user,
                status='in_progress'
            ).count(),
            'overdue_projects': Project.objects.filter(
                created_by=request.user,
                status='in_progress'
            ).filter(
                approved_end_date__lt=timezone.now().date()
            ).count(),
            'pending_approvals': pending_approvals,
        })
    
    return context