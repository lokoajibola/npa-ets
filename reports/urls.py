# reports/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.report_list, name='report_list'),
    path('projects/', views.project_reports, name='project_reports'),
    path('financial/', views.financial_reports, name='financial_reports'),
    path('status/', views.status_reports, name='status_reports'),
    path('generate/<str:report_type>/', views.generate_report, name='generate_report'),
]