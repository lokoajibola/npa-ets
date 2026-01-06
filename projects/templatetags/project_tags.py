from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def status_badge(status):
    badge_colors = {
        'draft': 'secondary',
        'submitted': 'info',
        'under_review': 'warning',
        'approved': 'primary',
        'in_progress': 'info',
        'on_hold': 'warning',
        'completed': 'success',
        'cancelled': 'danger',
        'pending': 'secondary',
        'requires_approval': 'warning',
        'blocked': 'danger',
    }
    return badge_colors.get(status, 'secondary')

@register.filter
def priority_badge(priority):
    badge_colors = {
        'low': 'success',
        'medium': 'warning',
        'high': 'danger',
        'critical': 'dark',
    }
    return badge_colors.get(priority, 'secondary')

@register.filter
def status_color(status):
    colors = {
        'pending': 'secondary',
        'in_progress': 'primary',
        'completed': 'success',
        'blocked': 'danger',
        'requires_approval': 'warning',
    }
    return colors.get(status, 'secondary')

@register.filter
def doc_icon(doc_type):
    icons = {
        'proposal': 'text',
        'feasibility_study': 'text',
        'tor': 'text',
        'boq': 'spreadsheet',
        'technical_spec': 'text',
        'tender_doc': 'text',
        'contract': 'text',
        'progress_report': 'text',
        'payment_cert': 'text',
        'completion_cert': 'text',
        'inspection_report': 'text',
        'other': 'text',
    }
    return icons.get(doc_type, 'text')

@register.filter
def div(value, arg):
    """Divide the value by the argument"""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return None

@register.filter
def mul(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return None