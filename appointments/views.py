from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login,logout
from django.conf import settings
from datetime import date, time
from django.contrib import auth
from django.contrib.auth.models import User, Group
from FaceRecognition.forms import VisitorRegistrationForm, VisitorUpdateForm, ManagerRegistrationForm, ManagerUpdateForm, FeedbackForm
from django.utils import timezone
from FaceRecognition.models import Visitor,Manager, ManagerAppointments
from appointments.models import Appointment
from django.contrib import messages
import datetime
from django.core.mail import send_mail, mail_admins
from appointments.forms import VisitorAppointmentForm
from django.urls import reverse


def profile_visitor_view(request):
    
    if check_visitor(request.user):
        
        # get information from database and render in html webpage
        vis = Visitor.objects.filter(visitor=request.user.id).first()
        if vis is not None:
            dob = vis.dob
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))  # calculate age
            if request.method == "POST":
                visitor_update_form = VisitorUpdateForm(request.POST, request.FILES, instance=vis)
                if visitor_update_form.is_valid():  # if form is valid
                    dob = visitor_update_form.cleaned_data.get('dob')  # get date of birth from form
                    today = date.today()
                    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                    if dob < timezone.now().date():  # if date of birth is valid
                        visitor_update_form.save()  # save details
                        vis.save()

                        messages.add_message(request, messages.INFO, 'Profile updated successfully!')
                        return redirect('profile_visitor.html')
                    else:
                        visitor_update_form.add_error('dob', 'Invalid date of birth.')
                        context = {
                            'visitor_update_form': visitor_update_form,
                            'vis': vis,
                            'age': age
                        }
                        return render(request, 'visitor/profile_visitor.html', context)
                else:
                    print(visitor_update_form.errors)
            visitor_update_form = VisitorUpdateForm(instance=vis)
            context = {
                'visitor_update_form': visitor_update_form,
                'vis': vis,
                'age': age
            }
            return render(request, 'visitor/profile_visitor.html', context)
        return redirect('index')
    else:
        auth.logout(request)
        return redirect('index')

def book_app_visitor_view(request):
    if check_visitor(request.user):
        vis = Visitor.objects.filter(visitor=request.user.id).first()
        app_details = []

        for app in Appointment.objects.filter(visitor=vis, status=False).all():
            e = app.manager
            if e:
                app_details.append([e.first_name, e.last_name, e.role,
                                    app.description, app.appointment_date, app.appointment_time, app.status])

        if request.method == "POST":  # if visitor books an appointment
            app_form = VisitorAppointmentForm(request.POST)

            if app_form.is_valid():  # if form is valid
                eng_id = int(app_form.cleaned_data.get('manager'))  # get manager id from form
                eng = Manager.objects.all().filter(id=eng_id).first()  # get manager from form

                if check_eng_availability(eng,  # check if manager is available during that slot
                                          app_form.cleaned_data.get('app_date'),
                                          app_form.cleaned_data.get('app_time')):
                    app_date = app_form.cleaned_data.get('app_date')  # get appointment date
                    if timezone.now().date() < app_date:  # check if appointment date is valid
                        app = Appointment(manager=eng,
                                          visitor=vis,
                                          description=app_form.cleaned_data.get('description'),
                                          appointment_date=app_form.cleaned_data.get('app_date'),
                                          appointment_time=app_form.cleaned_data.get('app_time'),
                                          status=False)  # create appointment instance, which is unapproved
                        app.save()
                        messages.add_message(request, messages.INFO, 'Your appointment is received and pending.')
                        return redirect('book_app_vis.html')
                    else:
                        app_form.add_error('app_date', 'Invalid date.')
                else:  # if manager is busy
                    app_form.add_error('app_time', 'Slot Unavailable.')
                return render(request, 'visitor/book_app_vis.html',
                              {'app_form': app_form, 'app_details': app_details})
            else:  # if form is invalid
                print(app_form.errors)
        else:
            app_form = VisitorAppointmentForm()
        return render(request, 'visitor/book_app_vis.html',
                      {'vis': vis, 'app_form': app_form, 'app_details': app_details})
    else:
        auth.logout(request)
        return redirect('login_vis.html')

def app_visitor_view(request):
    if check_visitor(request.user):
        # get information from database and render in html webpage
        vis = Visitor.objects.filter(visitor=request.user.id).first()

        total_app = Appointment.objects.filter(visitor=vis).count()
        total_approved_app = Appointment.objects.filter(status=True, visitor=vis).count()
        total_pending_app = Appointment.objects.filter(status=False, visitor=vis).count()
        # app_total = Appointment.objects.filter(status=True, visitor=vis).all()

        pending_appointment_details = []
        for app in Appointment.objects.filter(status=False, completed=False,
                                              visitor=vis).all():  # get all approved appointments
            e = app.manager
            c = app.visitor
            if e and c:
                pending_appointment_details.append(
                    [e.first_name, e.last_name, e.role, c.first_name, c.last_name,
                     app.pk, app.description, app.appointment_date, app.appointment_time,
                     app.status, app.completed, app.rating])

        incomplete_appointment_details = []
        for app in Appointment.objects.filter(status=True, completed=False,
                                              visitor=vis).all():  # get all approved appointments
            e = app.manager
            c = app.visitor
            if e and c:
                incomplete_appointment_details.append(
                    [e.first_name, e.last_name, e.role, c.first_name, c.last_name,
                     app.pk, app.description, app.appointment_date, app.appointment_time,
                     app.status, app.completed, app.rating])

        appointment_details = []
        for app in Appointment.objects.filter(status=True, visitor=vis).all():  # get all approved appointments
            e = app.manager
            c = app.visitor
            if e and c:
                appointment_details.append([e.first_name, e.last_name, e.role, c.first_name, c.last_name,
                                            app.pk, app.description, app.appointment_date, app.appointment_time, 
                                            app.status, app.completed, app.rating])

        messages.add_message(request, messages.INFO, 'You have {0} pending appointments.'.format(total_pending_app))

        context = {
            'vis': vis,
            'total_app': total_app,
            'total_approved_app': total_approved_app,
            'total_pending_app': total_pending_app,
            'pending_appointment_details': pending_appointment_details,
            'appointment_details': appointment_details,
            'incomplete_appointment_details': incomplete_appointment_details,
            # 'message': message
        }

        return render(request, 'visitor/view_app_vis.html',
                      context)
    else:
        auth.logout(request)
        return redirect('login_vis.html')

def all_app_visitors_view(request):
    if check_visitor(request.user):
        # get information from database and render in html webpage
        vis = Visitor.objects.filter(visitor=request.user.id).first()

        total_app = Appointment.objects.filter(visitor=vis).count()
        total_approved_app = Appointment.objects.filter(status=True, visitor=vis).count()
        total_pending_app = Appointment.objects.filter(status=False, visitor=vis).count()
        # app_total = Appointment.objects.filter(status=True, visitor=vis).all()

        pending_appointment_details = []
        for app in Appointment.objects.filter(status=False, completed=False,
                                              visitor=vis).all():  # get all approved appointments
            e = app.manager
            c = app.visitor
            if e and c:
                pending_appointment_details.append(
                    [e.first_name, e.last_name, e.role, c.first_name, c.last_name,
                     app.pk, app.description, app.appointment_date, app.appointment_time,
                     app.status, app.completed, app.rating])

        incomplete_appointment_details = []
        for app in Appointment.objects.filter(status=True, completed=False,
                                              visitor=vis).all():  # get all approved appointments
            e = app.manager
            c = app.visitor
            if e and c:
                incomplete_appointment_details.append(
                    [e.first_name, e.last_name, e.role, c.first_name, c.last_name,
                     app.pk, app.description, app.appointment_date, app.appointment_time,
                     app.status, app.completed, app.rating])

        completed_appointment_details = []
        for app in Appointment.objects.filter(status=True, completed=True,
                                              visitor=vis).all():  # get all approved appointments
            e = app.manager
            c = app.visitor
            if e and c:
                completed_appointment_details.append(
                    [e.first_name, e.last_name, e.role, c.first_name, c.last_name,
                     app.pk, app.description, app.appointment_date, app.appointment_time,
                     app.status, app.completed, app.rating])

        messages.add_message(request, messages.INFO, 'You have {0} appointments.'.format(total_approved_app))

        context = {
            'vis': vis,
            'total_app': total_app,
            'total_approved_app': total_approved_app,
            'total_pending_app': total_pending_app,
            'pending_appointment_details': pending_appointment_details,
            'completed_appointment_details': completed_appointment_details,
            'incomplete_appointment_details': incomplete_appointment_details,
        }

        return render(request, 'visitor/view_all_app_vis.html',
                      context)
    else:
        auth.logout(request)
        return redirect('login_vis.html')

def completed_app_visitors_view(request):
    if check_visitor(request.user):
        # get information from database and render in html webpage
        vis = Visitor.objects.filter(visitor=request.user.id).first()

        total_app = Appointment.objects.filter(visitor=vis).count()
        total_approved_app = Appointment.objects.filter(status=True, visitor=vis).count()
        total_pending_app = Appointment.objects.filter(status=False, visitor=vis).count()
        # app_total = Appointment.objects.filter(status=True, visitor=vis).all()

        completed_appointment_details = []
        for app in Appointment.objects.filter(status=True, completed=True,
                                              visitor=vis).all():  # get all approved appointments
            e = app.manager
            c = app.visitor
            if e and c:
                completed_appointment_details.append(
                    [e.first_name, e.last_name, e.role, c.first_name, c.last_name,
                     app.pk, app.description, app.appointment_date, app.appointment_time,
                     app.status, app.completed, app.rating])

        messages.add_message(request, messages.INFO, 'You have {0} appointments.'.format(total_approved_app))

        context = {
            'vis': vis,
            'total_app': total_app,
            'total_approved_app': total_approved_app,
            'total_pending_app': total_pending_app,
            'completed_appointment_details': completed_appointment_details,
        }

        return render(request, 'visitor/completed_app_visitor.html',
                      context)
    else:
        auth.logout(request)
        return redirect('login_vis.html')


def app_details_visitors_view(request, pk):
    if check_visitor(request.user):
        app = Appointment.objects.filter(id=pk).first()  # get appointment
        if app is not None:
            eng = app.manager
            vis = app.visitor

            appointment_details = [eng.first_name, eng.last_name, eng.role,
                                vis.first_name, vis.last_name,
                                vis.postcode, vis.city, vis.country,
                                app.appointment_date, app.appointment_time, app.description,
                                app.status, app.completed, pk]  # render fields
            return render(request, 'visitor/view_app_details_vis.html',
                        {
                        'eng': eng,
                        'app': app,
                        'vis': vis,
                        'appointment_details': appointment_details})
        return render(request, 'error.html')

        # 'med': med})
    else:
        auth.logout(request)
        return redirect('login_vis.html')

def app_report_visitors_view(request, pk):
    # get information from database and render in html webpage
    app = Appointment.objects.all().filter(id=pk).first()
    if app is not None:
        vis = app.visitor
        eng = app.manager
        app_date = app.appointment_date
        app_time = app.appointment_time

        app_details = []

        context = {
            'vis_name': vis.first_name,
            'eng_name': eng.first_name,
            'app_date': app_date,
            'app_time': app_time,
            'app_desc': app.description,
            'app_details': app_details,
            'pk': pk,
        }

        if check_visitor(request.user):
            return render(request, 'appointments/visitor/app_report_vis.html', context)
        else:
            return render(request, 'appointments/account/login.html')

def feedback_visitor_view(request):
    if check_visitor(request.user):
        vis = Visitor.objects.get(visitor=request.user.id)
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

                    return redirect('feedback_vis.html')
                except:
                    feedback_form.add_error('Email',
                                            'Try again.')
                    return render(request, 'visitor/feedback_vis.html', {'email': email,
                                                                                        'name': name,
                                                                                        'subject': subject,
                                                                                        'message': message,
                                                                                        'feedback_form': feedback_form,
                                                                                        'vis': vis})
        return render(request, 'visitor/feedback_vis.html', {'feedback_form': feedback_form,
                                                                                        'vis': vis})
    else:
        auth.logout(request)
        return redirect('login_vis.html')

def check_visitor(user):  # check if user is visitor
    return user.groups.filter(name='Visitor').exists()

def check_manager(user):  # check if user is manager
    return user.groups.filter(name='Manager').exists()

def check_eng_availability(manager, dt, tm):  # check if manager is available in a given slot
    hour, minute = tm.split(':')
    ftm = time(int(hour), int(minute), 0)
    app = Appointment.objects.all().filter(status=True,
                                           manager=manager,
                                           appointment_date=dt)  # get all appointments for a given eng and the given date

    if ftm < time(9, 0, 0) or ftm > time(17, 0, 0):  # if time is not in between 9AM to 5PM, reject
        return False

    if time(12, 0, 0) < ftm < time(13, 0, 0):  # if time is in between 12PM to 1PM, reject
        return False

    for a in app:
        if ftm == a.appointment_time and dt == a.appointment_date:  # if some other appointment has the same slot, reject
            return False

    return True

#MANAGER

def dashboard_mgr_view(request):
    if check_manager(request.user):
        adm = Manager.objects.filter(manager=request.user.id).first()
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
            for app in Appointment.objects.filter(status=False, manager=adm.pk,
                                                completed=False).all():  # get unapproved appointments which have links not set and are not yet finished
                c = Visitor.objects.filter(id=app.visitor.pk).first()
                if c:
                    pending_app.append([app.pk, c.first_name, c.last_name,
                                        app.appointment_date, app.appointment_time, app.description, app.status, app.completed])

            upcoming_app = []
            for app in Appointment.objects.filter(status=True, manager = adm.pk,
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

        context = {'adm': adm, 'app': app,
                   'adm_total': adm_total, 'cust_total': cust_total,  'app_total': app_total,
                   'pending_app_total': pending_app_total, 'app_count':app_count, 'app_completed':app_completed, 'available_app':available_app}  # render information

        return render(request, 'manager/dashboard_mgr.html', context)
    else:
        auth.logout(request)
        return redirect('index')


def profile_mgr_view(request):
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
                return render(request, 'manager/profile_mgr.html', context)
        return render(request, 'manager/profile_mgr.html')
            
    else:
        auth.logout(request)
        return redirect('')

def all_app_mgr_view(request):
    if check_manager(request.user):
        # get information from database and render in html webpage
        eng = Manager.objects.get(manager=request.user.id)
        app_completed = Appointment.objects.all().filter(manager=eng.pk, completed=True).count()
        available_app = Appointment.objects.all().filter(manager=eng.pk, status=False).count()
        app_count = Appointment.objects.all().filter(manager=eng.pk, status=True,).count()

        pending_app = []
        for app in Appointment.objects.filter(status=False, manager=eng.pk,
                                              completed=False).all():  # get unapproved appointments which have links not set and are not yet finished
            c = Visitor.objects.filter(id=app.visitor.pk).first()
            if c:
                pending_app.append([app.pk, c.first_name, c.last_name, 
                                    app.appointment_date, app.appointment_time, app.description, app.status, app.completed])

        upcoming_app = []
        for app in Appointment.objects.filter(status=True, manager=eng.pk, 
                                              completed=False).all():  # get approved appointments which have links not set and are not yet finished
            c = Visitor.objects.filter(id=app.visitor.pk).first()
            if c:
                upcoming_app.append([app.pk, c.first_name, c.last_name,
                                     app.appointment_date, app.appointment_time, app.description, app.status,
                                     app.completed,
                                     eng.first_name])

        completed_app = []  # approved manually inside
        for app in Appointment.objects.filter(manager=eng.pk, completed=True).all():  # get all approved appointments
            c = app.visitor
            if c:
                completed_app.append([app.pk, c.first_name, c.last_name, 
                                      app.appointment_date, app.appointment_time, app.description, app.status,
                                      app.completed,
                                      eng.first_name])

        return render(request, 'manager/view_app_mgr.html', {
            'eng': eng,
            'pending_app': pending_app,
            'upcoming_app': upcoming_app,
            'completed_app': completed_app,
            'app_completed': app_completed,
            'app_count': app_count,
            'available_app': available_app, })
    else:
        auth.logout(request)
        return redirect('login_eng.html')

def app_details_mgr_view(request, pk):
    if check_manager(request.user):
        adm = Manager.objects.filter(manager=request.user.id).first()

        app = Appointment.objects.filter(id=pk).first()  # get appointment
        if app is not None:
            eng = app.manager
            cust = app.visitor


            appointment_details = [eng.first_name, eng.last_name, eng.role,
                                cust.first_name, cust.last_name,
                                cust.postcode, cust.city, cust.country,
                                app.appointment_date, app.appointment_time, app.description,
                                app.status, app.completed, pk]  # render fields

            return render(request, 'manager/view_app_details_mgr.html',
                        {'adm': adm,
                        'eng': eng,
                        'app': app,
                        'cust': cust,
                        'appointment_details': appointment_details})
        return redirect('manager_appointments')
    else:
        auth.logout(request)
        return redirect('login_adm.html')



def get_link_mgr_action(request, pk):
    if check_manager(request.user):
        # get information from database
        appointment = Appointment.objects.get(id=pk)
        appointment.status = True  # approve appointment
        appointment.save()

        eng = appointment.manager
        esf = ManagerAppointments.objects.filter(manager=eng).first()
        if esf is not None:
            esf.app_total += 1  # add customer to engineer count
            esf.save()

        messages.add_message(request, messages.INFO, 'Appointment approved!')
        return redirect(reverse('dashboard_eng.html'))
    else:
        auth.logout(request)
        return redirect('login_eng.html')

def completed_meetings():
    return

def contact_us(request):
    return render(request, 'visitor/contact.html')