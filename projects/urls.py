from django.urls import path, register_converter
from . import views
from . import converters

register_converter(converters.ProjectIDConverter, 'projectid')

urlpatterns = [
    # Project List and Detail
    path('create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('', views.ProjectListView.as_view(), name='project_list'),
    path('contractors/', views.contractor_list, name='contractor_list'),
    path('contractors/add/', views.contractor_create, name='contractor_create'),
    # Budget URLs
    path('budgets/', views.budget_list_view, name='budget_list'),
    path('budgets/create/', views.budget_create_view, name='budget_create'),
    path('budgets/<uuid:budget_id>/', views.budget_detail_view, name='budget_detail'),
    path('budgets/<uuid:budget_id>/items/', views.budget_items_view, name='budget_items'),
    
    # API
    path('api/budgets/by-department/', views.api_budgets_by_department, name='api_budgets_by_department'),

    path('contractors/<uuid:contractor_id>/', views.contractor_detail, name='contractor_detail'),
    path('contractors/<uuid:contractor_id>/edit/', views.contractor_update, name='contractor_update'),
    path('<str:project_id>/', views.ProjectDetailView.as_view(), name='project_detail'),
    
    
    
    path('<str:project_id>/update/', views.ProjectUpdateView.as_view(), name='project_update'),
    
    # Project Stages
    path('<str:project_id>/stage/<uuid:stage_id>/', views.update_stage, name='update_stage'),

    # Replace generic stage URL with specific ones
    path('<str:project_id>/stage/site-inspection/<uuid:stage_id>/', 
        views.site_inspection_view, name='site_inspection'),
    path('<str:project_id>/stage/project-proposal/<uuid:stage_id>/', 
        views.project_proposal_view, name='project_proposal'),
    path('<str:project_id>/stage/contract-award/<uuid:stage_id>/', 
        views.contract_award_view, name='contract_award'),
    # Add more for each stage type
    # Replace or add these specific stage URLs
    path('<str:project_id>/stage/boq-beme/<uuid:stage_id>/', 
        views.boq_beme_view, name='boq_beme'),
    path('<str:project_id>/stage/boq-beme/<uuid:stage_id>/pdf/', 
     views.generate_beme_pdf, name='beme_pdf'),
    
    path('<str:project_id>/stage/due-diligence/<uuid:stage_id>/', 
        views.due_diligence_view, name='due_diligence'),
    path('<str:project_id>/stage/project-certification/<uuid:stage_id>/', 
        views.project_certification_view, name='project_certification'),
    path('<str:project_id>/stage/contract-award/<uuid:stage_id>/', 
        views.contract_award_view, name='contract_award'),
    path('<str:project_id>/stage/nomination-supervisor/<uuid:stage_id>/', 
        views.nomination_supervisor_view, name='nomination_supervisor'),

    path('<str:project_id>/certificate/<uuid:certificate_id>/pdf/', 
     views.certificate_pdf_view, name='certificate_pdf'),
    
    
    # Project Documents
    path('<str:project_id>/documents/', views.project_documents, name='project_documents'),
    path('<str:project_id>/documents/upload/', views.upload_document, name='upload_document'),
    
    # Progress Reports
    path('<str:project_id>/reports/', views.progress_reports, name='progress_reports'),
    path('<str:project_id>/reports/create/', views.create_progress_report, name='create_progress_report'),
    
    # Quick actions
    path('<str:project_id>/submit/', views.submit_project, name='submit_project'),
    path('<str:project_id>/approve/', views.approve_project, name='approve_project'),
    path('<str:project_id>/complete/', views.complete_project, name='complete_project'),
]