from django.urls import path
from . import views

urlpatterns = [
    #Visitor
    path('visitor/profile', views.profile_visitor_view, name='visitor_profile'), # Visitor profile 
    path('visitor/book-appointment', views.book_app_visitor_view, name='book_appointment'),  # Book an appointment
    path('visitor/appointments', views.app_visitor_view, name='visitor_appointments'),  # View pending appointments
    path('visitor/appointments/all', views.all_app_visitors_view, name='all_visitor_appointments'),  # View pending appointments
    path('visitor/appointment-details/<int:pk>', views.app_details_visitors_view, name='visitor_appointment_details'),  # View appointment details
    path('visitor/feedback/', views.feedback_visitor_view, name='visitor_feedback'),
    path('visitor/completed-appointments', views.completed_app_visitors_view, name='visitor_completed_appointments'),  # View pending appointments
    path('visitor/contact/', views.contact_us, name='contact_us'),
    
    #Manager
    path('manager/profile', views.profile_mgr_view, name='profile_manager'),  # Manager profile
    path('manager/dashboard', views.dashboard_mgr_view, name='manager_dashboard'),  # Manager dashboard
    path('manager/your-appointments/', views.all_app_mgr_view, name='manager_appointments'),  # View manager's appointments
    path('manager/appointment/get=<int:pk>', views.get_link_mgr_action, name='get_link_eng_action'),  # manager get appointment link action
    path('manager/appointment-details/<int:pk>', views.app_details_mgr_view, name='manager_appointment_details'),  # manager appointment's details
]