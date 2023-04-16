from django.urls import path, include
from . import views

urlpatterns = [
    path('register',views.register),
    path('face_recognition/',views.face_recognition),
    path('login/', views.login),
    path('dashboard/', views.dashboard),
    path('create_dataset/', views.create_dataset)
]