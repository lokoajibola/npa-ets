# approvals/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.approval_list, name='approval_list'),
    path('<str:approval_type>/<uuid:object_id>/', views.approval_detail, name='approval_detail'),
    path('<str:approval_type>/<uuid:object_id>/approve/', views.approve_item, name='approve_item'),
    path('<str:approval_type>/<uuid:object_id>/reject/', views.reject_item, name='reject_item'),
]