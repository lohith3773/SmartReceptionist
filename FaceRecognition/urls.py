from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('register/', views.register_visitor_view, name='register'), # Register Visitor
    path('login/',views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.home, name=''),
    path('train/',views.trainn),
    path('index/',views.index, name='index'),
    path('logout/',views.logout_view, name='logout'),
    path('profile/visitor/', views.profile_visitor_view, name='profile_visitor.html'),  # Visitor profile 
    path('visitor/book-appointment', views.book_app_cust_view, name='book_app_cust.html'),  # Book an appointment
    path('visitor/appointments', views.app_visitor_view, name='view_app_cust.html'),  # View pending appointments
    path('visitor/appointments/all', views.all_app_visitors_view, name='view_all_app_cust.html'),  # View pending appointments
    path('visitor/feedback/', views.feedback_visitor_view, name='feedback_cust.html'),
    path('visitor-appointment/details/<int:pk>', views.app_details_visitors_view, name='view_app_details_cust.html'),  # View appointment details

    #
]