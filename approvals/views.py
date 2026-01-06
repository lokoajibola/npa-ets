# approvals/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

@login_required
def approval_list(request):
    """List all pending approvals for the user"""
    context = {
        'page_title': 'Pending Approvals',
        'pending_approvals': [],
    }
    return render(request, 'approvals/approval_list.html', context)

@login_required
def approval_detail(request, approval_type, object_id):
    """View details of a specific approval item"""
    context = {
        'page_title': 'Approval Details',
        'approval_type': approval_type,
        'object_id': object_id,
    }
    return render(request, 'approvals/approval_detail.html', context)

@login_required
def approve_item(request, approval_type, object_id):
    """Approve an item"""
    messages.success(request, f'Item approved successfully!')
    return redirect('approval_list')

@login_required
def reject_item(request, approval_type, object_id):
    """Reject an item"""
    messages.warning(request, f'Item rejected.')
    return redirect('approval_list')