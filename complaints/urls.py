# # complaints/urls.py - Make sure all URLs are included
# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.home, name='home'),
#     path('dashboard/', views.dashboard, name='dashboard'),
    
#     # Admin URLs
#     path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
#     path('admin/users/', views.admin_user_management, name='admin_user_management'),
#     path('admin/users/create/', views.admin_create_user, name='admin_create_user'),
#     path('admin/users/<int:user_id>/edit/', views.admin_edit_user, name='admin_edit_user'),
#     path('admin/users/<int:user_id>/toggle/', views.admin_toggle_user, name='admin_toggle_user'),
#     path('admin/locations/', views.admin_location_management, name='admin_location_management'),
#     path('admin/reports/advanced/', views.advanced_reports, name='advanced_reports'),
    
#     # Authority URLs
#     path('authority/dashboard/', views.authority_dashboard, name='authority_dashboard'),
    
#     # Complaint URLs
#     path('complaints/create/', views.create_complaint, name='create_complaint'),
#     path('complaints/<int:complaint_id>/', views.complaint_detail, name='complaint_detail'),
#     path('complaints/<int:complaint_id>/update/', views.update_complaint_status, name='update_complaint_status'),
#     path('complaints/<int:complaint_id>/feedback/', views.submit_feedback, name='submit_feedback'),
#     path('complaints/', views.complaint_list, name='complaint_list'),
#     path('reports/', views.generate_reports, name='generate_reports'),
# ]



































# complaints/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Admin URLs - REMOVE 'admin/' prefix to avoid conflict
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-users/', views.admin_user_management, name='admin_user_management'),
    path('admin-users/create/', views.admin_create_user, name='admin_create_user'),
    path('admin-users/<int:user_id>/edit/', views.admin_edit_user, name='admin_edit_user'),
    path('admin-users/<int:user_id>/toggle/', views.admin_toggle_user, name='admin_toggle_user'),
    path('admin-locations/', views.admin_location_management, name='admin_location_management'),
    path('admin-reports/advanced/', views.advanced_reports, name='advanced_reports'),  # CHANGED
    
    # Authority URLs
    path('authority/dashboard/', views.authority_dashboard, name='authority_dashboard'),
    
    # Complaint URLs
    path('complaints/create/', views.create_complaint, name='create_complaint'),
    path('complaints/<int:complaint_id>/', views.complaint_detail, name='complaint_detail'),
    path('complaints/<int:complaint_id>/update/', views.update_complaint_status, name='update_complaint_status'),
    path('complaints/<int:complaint_id>/feedback/', views.submit_feedback, name='submit_feedback'),
    path('complaints/', views.complaint_list, name='complaint_list'),
    path('reports/', views.generate_reports, name='generate_reports'),
    path('debug-role/', views.debug_role, name='debug_role'),
    
]