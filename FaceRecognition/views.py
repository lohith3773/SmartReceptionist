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
                
                # group, created = Group.objects.get_or_create(name='Visitor')  # add user to group
                # group[0].user_set.add(new_user)
                
                messages.add_message(request, messages.INFO, 'Registration successful!')
                return redirect('login_cust.html')

            else:  # if date of birth is invalid
                registration_form.add_error('dob', 'Invalid date of birth.')
                print('dob error')
                return render(request, 'appointments/visitor/register_cust.html',{'registration_form': registration_form})
        else:
            print(registration_form.errors)
    else:
        registration_form = VisitorRegistrationForm()
    return render(request, 'appointments/visitor/register_cust.html', {'registration_form': registration_form})

def profile_visitor_view(request):
    
    if check_visitor(request.user):
        
        # get information from database and render in html webpage
        cust = Visitor.objects.filter(visitor=request.user.id).first()
        if cust is not None:
            dob = cust.dob
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))  # calculate age
            if request.method == "POST":
                visitor_update_form = VisitorUpdateForm(request.POST, request.FILES, instance=cust)
                if visitor_update_form.is_valid():  # if form is valid
                    dob = visitor_update_form.cleaned_data.get('dob')  # get date of birth from form
                    today = date.today()
                    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                    if dob < timezone.now().date():  # if date of birth is valid
                        visitor_update_form.save()  # save details
                        cust.save()

                        messages.add_message(request, messages.INFO, 'Profile updated successfully!')
                        return redirect('profile_visitor.html')
                    else:
                        visitor_update_form.add_error('dob', 'Invalid date of birth.')
                        context = {
                            'visitor_update_form': visitor_update_form,
                            'cust': cust,
                            'age': age
                        }
                        return render(request, 'visitor/profile_visitor.html', context)
                else:
                    print(visitor_update_form.errors)
            visitor_update_form = VisitorUpdateForm(instance=cust)
            context = {
                'visitor_update_form': visitor_update_form,
                'cust': cust,
                'age': age
            }
            return render(request, 'visitor/profile_visitor.html', context)
        return redirect('login.html')
    else:
        auth.logout(request)
        return redirect('login.html')

def book_app_cust_view(request):
    if check_visitor(request.user):
        cust = Visitor.objects.filter(visitor=request.user.id).first()
        app_details = []

        for app in Appointment.objects.filter(visitor=cust, status=False).all():
            e = app.manager
            if e:
                app_details.append([e.first_name, e.last_name, e.role,
                                    app.description, app.appointment_date, app.appointment_time, app.status])

        if request.method == "POST":  # if visitor books an appointment
            app_form = VisitorAppointmentForm(request.POST)

            if app_form.is_valid():  # if form is valid
                eng_id = int(app_form.cleaned_data.get('manager'))  # get engineer id from form
                eng = Manager.objects.all().filter(id=eng_id).first()  # get engineer from form

                if check_eng_availability(eng,  # check if engineer is available during that slot
                                          app_form.cleaned_data.get('app_date'),
                                          app_form.cleaned_data.get('app_time')):
                    app_date = app_form.cleaned_data.get('app_date')  # get appointment date
                    if timezone.now().date() < app_date:  # check if appointment date is valid
                        app = Appointment(manager=eng,
                                          visitor=cust,
                                          description=app_form.cleaned_data.get('description'),
                                          appointment_date=app_form.cleaned_data.get('app_date'),
                                          appointment_time=app_form.cleaned_data.get('app_time'),
                                          status=False)  # create appointment instance, which is unapproved
                        app.save()
                        messages.add_message(request, messages.INFO, 'Your appointment is received and pending.')
                        return redirect('book_app_cust.html')
                    else:
                        app_form.add_error('app_date', 'Invalid date.')
                else:  # if engineer is busy
                    app_form.add_error('app_time', 'Slot Unavailable.')
                return render(request, 'visitor/book_app_cust.html',
                              {'app_form': app_form, 'app_details': app_details})
            else:  # if form is invalid
                print(app_form.errors)
        else:
            app_form = VisitorAppointmentForm()
        return render(request, 'visitor/book_app_cust.html',
                      {'cust': cust, 'app_form': app_form, 'app_details': app_details})
    else:
        auth.logout(request)
        return redirect('login_cust.html')



def app_visitor_view(request):
    if check_visitor(request.user):
        # get information from database and render in html webpage
        cust = Visitor.objects.filter(visitor=request.user.id).first()

        total_app = Appointment.objects.filter(visitor=cust).count()
        total_approved_app = Appointment.objects.filter(status=True, visitor=cust).count()
        total_pending_app = Appointment.objects.filter(status=False, visitor=cust).count()
        # app_total = Appointment.objects.filter(status=True, visitor=cust).all()

        pending_appointment_details = []
        for app in Appointment.objects.filter(status=False, completed=False,
                                              visitor=cust).all():  # get all approved appointments
            e = app.manager
            c = app.visitor
            if e and c:
                pending_appointment_details.append(
                    [e.first_name, e.last_name, e.role, c.first_name, c.last_name,
                     app.pk, app.description, app.appointment_date, app.appointment_time,
                     app.status, app.completed, app.rating])

        incomplete_appointment_details = []
        for app in Appointment.objects.filter(status=True, completed=False,
                                              visitor=cust).all():  # get all approved appointments
            e = app.manager
            c = app.visitor
            if e and c:
                incomplete_appointment_details.append(
                    [e.first_name, e.last_name, e.role, c.first_name, c.last_name,
                     app.pk, app.description, app.appointment_date, app.appointment_time,
                     app.status, app.completed, app.rating])

        appointment_details = []
        for app in Appointment.objects.filter(status=True, visitor=cust).all():  # get all approved appointments
            e = app.manager
            c = app.visitor
            if e and c:
                appointment_details.append([e.first_name, e.last_name, e.role, c.first_name, c.last_name,
                                            app.pk, app.description, app.appointment_date, app.appointment_time, 
                                            app.status, app.completed, app.rating])

        messages.add_message(request, messages.INFO, 'You have {0} pending appointments.'.format(total_pending_app))

        context = {
            'cust': cust,
            'total_app': total_app,
            'total_approved_app': total_approved_app,
            'total_pending_app': total_pending_app,
            'pending_appointment_details': pending_appointment_details,
            'appointment_details': appointment_details,
            'incomplete_appointment_details': incomplete_appointment_details,
            # 'message': message
        }

        return render(request, 'visitor/view_app_cust.html',
                      context)
    else:
        auth.logout(request)
        return redirect('login_cust.html')

def all_app_visitors_view(request):
    if check_visitor(request.user):
        # get information from database and render in html webpage
        cust = Visitor.objects.filter(visitor=request.user.id).first()

        total_app = Appointment.objects.filter(visitor=cust).count()
        total_approved_app = Appointment.objects.filter(status=True, visitor=cust).count()
        total_pending_app = Appointment.objects.filter(status=False, visitor=cust).count()
        # app_total = Appointment.objects.filter(status=True, visitor=cust).all()

        pending_appointment_details = []
        for app in Appointment.objects.filter(status=False, completed=False,
                                              visitor=cust).all():  # get all approved appointments
            e = app.manager
            c = app.visitor
            if e and c:
                pending_appointment_details.append(
                    [e.first_name, e.last_name, e.role, c.first_name, c.last_name,
                     app.pk, app.description, app.appointment_date, app.appointment_time,
                     app.status, app.completed, app.rating])

        incomplete_appointment_details = []
        for app in Appointment.objects.filter(status=True, completed=False,
                                              visitor=cust).all():  # get all approved appointments
            e = app.manager
            c = app.visitor
            if e and c:
                incomplete_appointment_details.append(
                    [e.first_name, e.last_name, e.role, c.first_name, c.last_name,
                     app.pk, app.description, app.appointment_date, app.appointment_time,
                     app.status, app.completed, app.rating])

        completed_appointment_details = []
        for app in Appointment.objects.filter(status=True, completed=True,
                                              visitor=cust).all():  # get all approved appointments
            e = app.manager
            c = app.visitor
            if e and c:
                completed_appointment_details.append(
                    [e.first_name, e.last_name, e.role, c.first_name, c.last_name,
                     app.pk, app.description, app.appointment_date, app.appointment_time,
                     app.status, app.completed, app.rating])

        messages.add_message(request, messages.INFO, 'You have {0} appointments.'.format(total_approved_app))

        context = {
            'cust': cust,
            'total_app': total_app,
            'total_approved_app': total_approved_app,
            'total_pending_app': total_pending_app,
            'pending_appointment_details': pending_appointment_details,
            'completed_appointment_details': completed_appointment_details,
            'incomplete_appointment_details': incomplete_appointment_details,
        }

        return render(request, 'visitor/view_all_app_cust.html',
                      context)
    else:
        auth.logout(request)
        return redirect('login_cust.html')

def app_details_visitors_view(request, pk):
    if check_visitor(request.user):
        app = Appointment.objects.filter(id=pk).first()  # get appointment
        if app is not None:
            eng = app.manager
            cust = app.visitor

            appointment_details = [eng.first_name, eng.last_name, eng.role,
                                cust.first_name, cust.last_name,
                                cust.postcode, cust.city, cust.country,
                                app.appointment_date, app.appointment_time, app.description,
                                app.status, app.completed, pk]  # render fields
            return render(request, 'visitor/view_app_details_cust.html',
                        {
                        'eng': eng,
                        'app': app,
                        'cust': cust,
                        'appointment_details': appointment_details})
        return render(request, 'error.html')

        # 'med': med})
    else:
        auth.logout(request)
        return redirect('login_cust.html')

def app_report_visitors_view(request, pk):
    # get information from database and render in html webpage
    app = Appointment.objects.all().filter(id=pk).first()
    if app is not None:
        cust = app.visitor
        eng = app.manager
        app_date = app.appointment_date
        app_time = app.appointment_time

        app_details = []

        context = {
            'cust_name': cust.first_name,
            'eng_name': eng.first_name,
            'app_date': app_date,
            'app_time': app_time,
            'app_desc': app.description,
            'app_details': app_details,
            'pk': pk,
        }

        if check_visitor(request.user):
            return render(request, 'appointments/visitor/app_report_cust.html', context)
        else:
            return render(request, 'appointments/account/login.html')

def feedback_visitor_view(request):
    if check_visitor(request.user):
        cust = Visitor.objects.get(visitor=request.user.id)
        feedback_form = FeedbackForm()
        if request.method == 'POST':
            feedback_form = FeedbackForm(request.POST)
            if feedback_form.is_valid():  # if form is valid
                email = feedback_form.cleaned_data['Email']  # get email from form
                name = feedback_form.cleaned_data['Name']  # get name from form
                subject = "You have a new Feedback from {}:<{}>".format(name, feedback_form.cleaned_data[
                    'Email'])  # get subject from form
                message = feedback_form.cleaned_data['Message']  # get message from form

                message = "Subject: {}\n" \
                          "Date: {}\n" \
                          "Message:\n\n {}" \
                    .format(dict(feedback_form.subject_choices).get(feedback_form.cleaned_data['Subject']),
                            datetime.datetime.now(),
                            feedback_form.cleaned_data['Message'])

                try:
                    mail_admins(subject, message)
                    messages.add_message(request, messages.INFO, 'Thank you for submitting your feedback.')

                    return redirect('feedback_cust.html')
                except:
                    feedback_form.add_error('Email',
                                            'Try again.')
                    return render(request, 'visitor/feedback_cust.html', {'email': email,
                                                                                        'name': name,
                                                                                        'subject': subject,
                                                                                        'message': message,
                                                                                        'feedback_form': feedback_form,
                                                                                        'cust': cust})
        return render(request, 'visitor/feedback_cust.html', {'feedback_form': feedback_form,
                                                                                        'cust': cust})
    else:
        auth.logout(request)
        return redirect('login_cust.html')

#Manager 

def register_manager_view(request):  # Register manager
    if request.method == "POST":
        registration_form = ManagerRegistrationForm(request.POST, request.FILES)
        if registration_form.is_valid():  # if form is valid
            dob = registration_form.cleaned_data.get('dob')  # get date of birth from form
            if dob < timezone.now().date():  # if date of birth is valid
                new_user = User.objects.create_user(username=registration_form.cleaned_data.get('username'),
                                                    email=registration_form.cleaned_data.get('email'),
                                                    password=registration_form.cleaned_data.get(
                                                        'password1'))  # create new user
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

                # group = Group.objects.get_or_create(name='Engineer')  # add user to doctor group
                # group[0].user_set.add(new_user)

                messages.add_message(request, messages.INFO, 'Registration successful!')
                return redirect('login_eng.html')
            else:  # if date of birth is invalid
                registration_form.add_error('dob', 'Invalid date of birth.')
                return render(request, 'appointments/manager/register_eng.html',
                              {'registration_form': registration_form})
        else:
            print(registration_form.errors)
    else:
        registration_form = ManagerRegistrationForm()

    return render(request, 'appointments/manager/register_eng.html', {'registration_form': registration_form})

def dashboard_adm_view(request):
    if check_manager(request.user):
        adm = Manager.objects.filter(admin_id=request.user.id).first()
        adm_det = Manager.objects.all().filter(status=False)
        app = Appointment.objects.all().filter(status=False)  # get all on-hold appointments

        adm_total = Manager.objects.all().count()  # total visitors
        cust_total = Visitor.objects.all().count()  # total visitors
        app_total = Appointment.objects.all().count()  # get total appointments
        
        app_completed = Appointment.objects.all().filter(manager = adm, completed=True).count()
        available_app = Appointment.objects.all().filter(manager = adm, status=False).count()
        pending_app_count = Appointment.objects.all().filter(manager = adm, status=False).count()
        app_count = Appointment.objects.all().filter(status=True, manager = adm).count()

        if adm is not None:
            pending_app = []
            for app in Appointment.objects.filter(status=False, manager=adm.pk, app_link__isnull=True,
                                                completed=False).all():  # get unapproved appointments which have links not set and are not yet finished
                c = Visitor.objects.filter(id=app.visitor.pk).first()
                if c:
                    pending_app.append([app.pk, c.first_name, c.last_name,
                                        app.appointment_date, app.appointment_time, app.description, app.status, app.completed])

            upcoming_app = []
            for app in Appointment.objects.filter(status=True, manager = adm.pk, app_link__isnull=True,
                                                completed=False).all():  # get approved appointments which have links not set and are not yet finished
                c = Visitor.objects.filter(id=app.visitor.pk).first()
                if c:
                    upcoming_app.append([app.pk, c.first_name, c.last_name,
                                        app.appointment_date, app.appointment_time, app.description, app.status,
                                        app.completed,
                                        adm.first_name])

            completed_app = []  # approved manually inside
            for app in Appointment.objects.filter(manager=adm, completed=True).all():  # get all approved appointments
                c = app.visitor
                if c:
                    completed_app.append([adm.first_name,
                                        c.first_name,
                                        app.completed, app.pk])

            messages.add_message(request, messages.INFO, 'You have {0} pending appointments to approve.'.format(pending_app_count))

        pending_app_total = Appointment.objects.all().filter(status=False).count()  # get total onhold appointments

        messages.add_message(request, messages.INFO, 'There are {0} appointments that require approval.'.format(pending_app_total))

        context = {'adm': adm, 'app': app, 'adm_det': adm_det,
                   'adm_total': adm_total, 'cust_total': cust_total,  'app_total': app_total,
                   'pending_app_total': pending_app_total}  # render information

        return render(request, 'appointments/admin/dashboard_adm.html', context)
    else:
        auth.logout(request)
        return redirect('login_adm.html')


def profile_eng_view(request):
    if check_manager(request.user):
        # get information from database and render in html webpage
        eng = Manager.objects.filter(manager_id=request.user.id).first()
        if eng is not None:
            dob = eng.dob
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))  # calculate age
            if request.method == "POST":
                manager_update_form = ManagerUpdateForm(request.POST, request.FILES, instance=eng)
                if manager_update_form.is_valid():  # if form is valid
                    dob = manager_update_form.cleaned_data.get('dob')
                    today = date.today()
                    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))  # calculate age
                    if dob < timezone.now().date():  # if date of birth is valid
                        manager_update_form.save()

                        messages.add_message(request, messages.INFO, 'Profile updated successfully!')
                        return redirect('profile_eng.html')
                    else:
                        manager_update_form.add_error('dob', 'Invalid date of birth.')
                        context = {
                            'manager_update_form': manager_update_form,
                            'eng': eng,
                            'age': age
                        }
                        return render(request, 'appointments/manager/profile_eng.html', context)
            else:
                # get data from database and put initial values in form
                # age.refresh_from_db()
                manager_update_form = ManagerUpdateForm(instance=eng)
                context = {
                    'manager_update_form': manager_update_form,
                    'eng': eng,
                    'age': age
                }
                return render(request, 'appointments/manager/profile_eng.html', context)
    else:
        auth.logout(request)
        return redirect('login_eng.html')



def check_visitor(user):  # check if user is visitor
    return user.groups.filter(name='Visitor').exists()

def check_manager(user):  # check if user is manager
    return user.groups.filter(name='Manager').exists()

def check_eng_availability(engineer, dt, tm):  # check if engineer is available in a given slot
    hour, minute = tm.split(':')
    ftm = time(int(hour), int(minute), 0)
    app = Appointment.objects.all().filter(status=True,
                                           manager=engineer,
                                           appointment_date=dt)  # get all appointments for a given eng and the given date

    if ftm < time(9, 0, 0) or ftm > time(17, 0, 0):  # if time is not in between 9AM to 5PM, reject
        return False

    if time(12, 0, 0) < ftm < time(13, 0, 0):  # if time is in between 12PM to 1PM, reject
        return False

    for a in app:
        if ftm == a.appointment_time and dt == a.appointment_date:  # if some other appointment has the same slot, reject
            return False

    return True


def index(request):
    user = request.user
    return render(request, 'index.html',{'user':user})


def home(request):
    return render(request, 'home.html')

def trainn(request):
    train_model()
    return render(request, 'dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('home')

