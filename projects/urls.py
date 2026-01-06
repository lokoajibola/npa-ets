from django.urls import path
from . import views

urlpatterns = [
    # Project List and Detail
    path('', views.ProjectListView.as_view(), name='project_list'),
    path('<str:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('<str:pk>/update/', views.ProjectUpdateView.as_view(), name='project_update'),
    
    # Project Stages
    path('<str:project_id>/stage/<uuid:stage_id>/', views.update_stage, name='update_stage'),
    
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