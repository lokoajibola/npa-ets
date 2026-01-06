# reports/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def report_list(request):
    """List all available reports"""
    context = {
        'page_title': 'Reports',
    }
    return render(request, 'reports/report_list.html', context)

@login_required
def project_reports(request):
    """Project-related reports"""
    context = {
        'page_title': 'Project Reports',
    }
    return render(request, 'reports/project_reports.html', context)

@login_required
def financial_reports(request):
    """Financial reports"""
    context = {
        'page_title': 'Financial Reports',
    }
    return render(request, 'reports/financial_reports.html', context)

@login_required
def status_reports(request):
    """Status reports"""
    context = {
        'page_title': 'Status Reports',
    }
    return render(request, 'reports/status_reports.html', context)

@login_required
def generate_report(request, report_type):
    """Generate a specific report"""
    context = {
        'page_title': f'Generate {report_type} Report',
        'report_type': report_type,
    }
    return render(request, 'reports/generate_report.html', context)