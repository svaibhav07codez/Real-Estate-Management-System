from django.urls import path
from . import views

urlpatterns = [
    # Home and Dashboard
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/client/', views.client_dashboard, name='client_dashboard'),
    path('dashboard/agent/', views.agent_dashboard, name='agent_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    
    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profile Management
    path('profile/client/create/', views.client_profile_create, name='client_profile_create'),
    path('profile/client/update/', views.client_profile_update, name='client_profile_update'),
    path('profile/agent/create/', views.agent_profile_create, name='agent_profile_create'),
    path('profile/agent/update/', views.agent_profile_update, name='agent_profile_update'),
    
    # Property CRUD
    path('properties/', views.property_list_view, name='property_list'),
    path('properties/<int:pk>/', views.property_detail_view, name='property_detail'),
    path('properties/create/', views.property_create_view, name='property_create'),
    path('properties/<int:pk>/update/', views.property_update_view, name='property_update'),
    path('properties/<int:pk>/delete/', views.property_delete_view, name='property_delete'),
    
    # Appointment CRUD
    path('appointments/', views.appointment_list_view, name='appointment_list'),
    path('appointments/create/<int:property_pk>/', views.appointment_create_view, name='appointment_create'),
    path('appointments/<int:pk>/update/', views.appointment_update_view, name='appointment_update'),
    path('appointments/<int:pk>/delete/', views.appointment_delete_view, name='appointment_delete'),
    
    # Transaction CRUD
    path('transactions/', views.transaction_list_view, name='transaction_list'),
    path('transactions/<int:pk>/', views.transaction_detail_view, name='transaction_detail'),
    path('transactions/create/<int:property_pk>/', views.transaction_create_view, name='transaction_create'),
    
    # Review CRUD
    path('reviews/create/<int:property_pk>/', views.review_create_view, name='review_create'),
    path('reviews/<int:pk>/delete/', views.review_delete_view, name='review_delete'),
    
    # Analytics (Bonus)
    path('analytics/', views.analytics_view, name='analytics'),
]