from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login,logout
from .recognizer import create_dataset, train_model,recognize_face
import cv2
from keras.models import load_model
import pickle
from django.conf import settings
import numpy as np
from datetime import date, time
from django.contrib import auth
from django.contrib.auth.models import User, Group
from .forms import VisitorRegistrationForm, VisitorUpdateForm, ManagerRegistrationForm, ManagerUpdateForm, FeedbackForm
from django.utils import timezone
from .models import Visitor,Manager
from appointments.models import Appointment
from django.contrib import messages
import datetime
from django.core.mail import send_mail, mail_admins
from appointments.forms import VisitorAppointmentForm
from appointments.views import index

BASE_DIR = str(settings.BASE_DIR)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    passwordd = 'ww@123321'
    recognized_user = recognize_face() # call the recognize_face function
    # check if user is authenticated
    if recognized_user is not None:
        print(recognized_user)
        if(recognized_user == "lohi"):
            recognized_user = "Lohhhhhhhhhh"
        user = authenticate(request, username=recognized_user, password = passwordd)
        print(user)
        if user is not None:
            login(request, user)
            return redirect('index')
    
    return render(request, 'login.html')


def dashboard(request):
    return render(request, 'dashboard.html', {'name': request.user.username})

def register_visitor_view(request):
    if request.method == 'POST':
        # form = UserCreationForm(request.POST)
        registration_form = VisitorRegistrationForm(request.POST, request.FILES)

        if registration_form.is_valid():
            dob = registration_form.cleaned_data.get('dob')  # ger date of birth from form
            if dob < timezone.now().date():  # check if date is valid
                new_user = User.objects.create_user(username=registration_form.cleaned_data.get('username'),
                                                    email=registration_form.cleaned_data.get('email'),
                                                    password=registration_form.cleaned_data.get('password1'))
                v = Visitor(visitor=new_user,
                            first_name=registration_form.cleaned_data.get('first_name'),
                            last_name=registration_form.cleaned_data.get('last_name'),
                            dob=registration_form.cleaned_data.get('dob'),
                            address=registration_form.cleaned_data.get('address'),
                            email_address=registration_form.cleaned_data.get('email_address'),
                            city=registration_form.cleaned_data.get('city'),
                            postcode=registration_form.cleaned_data.get('postcode'),
                            country=registration_form.cleaned_data.get('country'),
                            image=request.FILES['image']
                            )
                v.save()
                create_dataset(new_user)
                mgrgroup = Group.objects.get(name = 'Visitor')
                new_user.groups.add(mgrgroup)
                login(request, new_user)
                
                messages.add_message(request, messages.INFO, 'Registration successful!')
                return redirect('profile_visitor')

            else:  # if date of birth is invalid
                registration_form.add_error('dob', 'Invalid date of birth.')
                print('dob error')
                return render(request, 'visitor/register_visitor.html',{'registration_form': registration_form})
        else:
            print(registration_form.errors)
    else:
        registration_form = VisitorRegistrationForm()
    return render(request, 'visitor/register_visitor.html', {'registration_form': registration_form})


#Manager 

def register_manager_view(request):  # Register manager
    if request.method == "POST":
        registration_form = ManagerRegistrationForm(request.POST, request.FILES)
        if registration_form.is_valid():  # if form is valid
            dob = registration_form.cleaned_data.get('dob')  # get date of birth from form
            if dob < timezone.now().date():  # if date of birth is valid
                new_user = User.objects.create_user(username=registration_form.cleaned_data.get('username'),
                                                    email=registration_form.cleaned_data.get('email'),
                                                    password=registration_form.cleaned_data.get('password1'))  # create new user
                eng = Manager(manager=new_user,
                               first_name=registration_form.cleaned_data.get('first_name'),
                               last_name=registration_form.cleaned_data.get('last_name'),
                               role=registration_form.cleaned_data.get('role'),
                               dob=registration_form.cleaned_data.get('dob'),
                               address=registration_form.cleaned_data.get('address'),
                               city=registration_form.cleaned_data.get('city'),
                               country=registration_form.cleaned_data.get('country'),
                               postcode=registration_form.cleaned_data.get('postcode'),
                               image=request.FILES['image'])  # create new manager
                eng.save()
                mgrgroup = Group.objects.get(name = 'Manager')
                new_user.groups.add(mgrgroup)
                
                login(request, new_user)
                
                messages.add_message(request, messages.INFO, 'Registration successful!')
                return redirect('profile_manager')
            else:  # if date of birth is invalid
                registration_form.add_error('dob', 'Invalid date of birth.')
                return render(request, 'appointments/manager/register_mgr.html',
                              {'registration_form': registration_form})
        else:
            print(registration_form.errors)
    else:
        registration_form = ManagerRegistrationForm()

    return render(request, 'manager/register_mgr.html', {'registration_form': registration_form})




def home(request):
    return render(request, 'home.html')

def trainn(request):
    train_model()
    return render(request, 'dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('')

def login_new_manager(request):
    user = authenticate(request,username = 'manager3',password ='ww@123321') 
    if user is not None:
        login(request, user)
        return redirect('profile_manager')
    return redirect('index')

def login_new_visitor(request):
    user = authenticate(request,username = 'Lohhhhhhhhhh',password ='ww@123321') 
    if user is not None:
        login(request, user)
        return redirect('visitor_profile')
    return redirect('index')
    