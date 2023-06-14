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
    path('register/manager', views.register_manager_view, name='register_manager'), # Register Visitor
    path('loginmgr', views.login_new_manager,name='mgr')   
]