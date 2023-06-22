from django.urls import path
from . import views

urlpatterns = [
    #Admin
    path('register/admin', views.register_adm_view, name='register_admin'), # Visitor profile 
    path('login/admin', views.login_adm_view, name='login_admin'), # Visitor profile 
    path('dashboard/admin/', views.dashboard_adm_view, name='admin_dashboard'),  # Admin dashboard
    path('profile/admin/', views.profile_adm_view, name='admin_profile'),  # Admin profile
    #Admin - Appointments
    path('view/appointments/', views.appointment_adm_view, name='appointment_admin'),  # Admin appointments
    path('book-appointment/admin', views.book_app_adm_view, name='book_app_admin'),  # Book an appointment
    path('download-report/', views.dl_report_adm_action, name="dl_report_adm_action"),
    path('approve-appointment/<int:pk>', views.approve_app_adm_action, name='approve_app_adm_action'),  # Approve an appointment
    path('appointments/all/', views.all_app_adm_view, name='view_all_app_admin'),  # View approved appointments
    path('appointment/details/<int:pk>', views.app_details_adm_view, name='view_app_details_admin'),  # View approved appointment's details
    path('appointment-admin/complete=<int:pk>', views.complete_app_adm_action, name='complete_app_adm_action'),  # Complete appointment action
    #Admin - Visitor
    path('view/visitor/', views.visitor_adm_view, name='admin_visitors'),  # Customers section
    #Admin - Manager
    path('view/managers/', views.manager_adm_view, name='admin_managers'),  # Engineers section
    path('approve/managers/', views.approve_mgr_adm_view, name='approve_manager'),  # Approve engineer accounts
    path('approve/manager=<int:pk>', views.approve_mgr_adm_action, name='approve_eng_action'), # Approve engineer action
    path('view/all-managers/', views.all_mgr_adm_view, name='view_all_mgr'),  # View all engineer accounts
    
    #Visitor
    path('visitor/profile', views.profile_visitor_view, name='visitor_profile'), # Visitor profile 
    path('visitor/book-appointment', views.book_app_visitor_view, name='book_app_visitor'),  # Book an appointment
    path('visitor/appointments', views.app_visitor_view, name='visitor_appointments'),  # View pending appointments
    path('visitor/appointments/all', views.all_app_visitors_view, name='all_visitor_appointments'),  # View pending appointments
    path('visitor/appointment-details/<int:pk>', views.app_details_visitors_view, name='visitor_appointment_details'),  # View appointment details
    path('visitor/feedback/', views.feedback_visitor_view, name='visitor_feedback'),
    path('visitor/completed-appointments', views.completed_app_visitors_view, name='visitor_completed_appointments'),  # View pending appointments
    path('contact/', views.contact_us, name='contact_us'),
    #Manager
    path('manager/profile', views.profile_mgr_view, name='profile_manager'),  # Manager profile
    path('manager/book-appointment', views.book_app_manager_view, name='book_app_manager'),  # Book an appointment
    path('manager/appointments', views.dashboard_mgr_view, name='manager_dashboard'),  # Manager dashboard
    path('manager/appointments/all', views.all_app_mgr_view, name='manager_appointments'),  # View manager's appointments
    path('manager/appointment-details/<int:pk>', views.app_details_mgr_view, name='manager_appointment_details'),  # manager appointment's details
    path('manager/appointment/get=<int:pk>', views.get_link_mgr_action, name='get_link_eng_action'),  # manager get appointment link action
    path('manager/completed-appointments', views.completed_app_managers_view, name='completed_app_manager'),  # View pending appointments
    path('manager/feedback/', views.feedback_manager_view, name='manager_feedback'),
    path('index/',views.index, name='index'),
    path('home',views.home,name="home")
]