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
from appointments.models import Appointment, ApprovedVisitorAppointment,Admin, Feedback
from django.contrib import messages
import datetime
from django.core.mail import send_mail, mail_admins
from appointments.forms import VisitorAppointmentForm, ManagerAppointmentForm, AdminRegistrationForm, AdminAppointmentForm, AdminUpdateForm
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

#ADMIN

def register_adm_view(request):  # register admin
    if request.method == "POST":
        registration_form = AdminRegistrationForm(request.POST, request.FILES)
        if registration_form.is_valid():  # get data from form (if it is valid)
            dob = registration_form.cleaned_data.get('dob')  # get date of birth from form
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))  # calculate age from dob
            if dob < timezone.now().date():  # check if date of birth is valid (happened the previous day or even back)
                new_user = User.objects.create_user(username=registration_form.cleaned_data.get('username'),
                                                    email=registration_form.cleaned_data.get('email'),
                                                    password=registration_form.cleaned_data.get(
                                                        'password1'))  # create user
                adm = Admin(admin=new_user,
                            first_name=registration_form.cleaned_data.get('first_name'),
                            last_name=registration_form.cleaned_data.get('last_name'),
                            # age=form.cleaned_data.get('age'),
                            dob=registration_form.cleaned_data.get('dob'),
                            address=registration_form.cleaned_data.get('address'),
                            city=registration_form.cleaned_data.get('city'),
                            country=registration_form.cleaned_data.get('country'),
                            postcode=registration_form.cleaned_data.get('postcode'),
                            )  # create admin
                adm.save()
                admgroup = Group.objects.get(name = 'Admin')
                new_user.groups.add(admgroup)

                messages.add_message(request, messages.INFO, 'Registration successful!')
                return redirect('login_admin')
            else:
                registration_form.add_error('dob', 'Invalid date of birth.')
        else:
            print(registration_form.errors)
            return render(request, 'adminTemp/register_adm.html', {'registration_form': registration_form})
    else:
        registration_form = AdminRegistrationForm()

    return render(request, 'adminTemp/register_adm.html', {'registration_form': registration_form})

def login_adm_view(request):  # login admin
    if request.method == "POST":
        login_form = AuthenticationForm(request=request, data=request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')  # get username
            password = login_form.cleaned_data.get('password')  # get password
            user = auth.authenticate(username=username, password=password)  # authenticate user
            if user is not None and check_admin(user):  # if user exists and is admin
                
                auth.login(request, user)  # login user
                account_approval = Admin.objects.all().filter(status=True,
                                                              admin_id=request.user.id)  # if account is approved
                if account_approval:
                    return redirect('admin_profile')
                    # return redirect('dashboard_adm.html')
                else:  # if account is not yet approved
                    auth.logout(request)
                    messages.add_message(request, messages.INFO, 'Your account is currently pending. '
                                                                 'Please wait for approval.')
                    return render(request, 'adminTemp/login_adm.html', {'login_form': login_form})
        return render(request, 'adminTemp/login_adm.html', {'login_form': login_form})
    else:
        login_form = AuthenticationForm()

    return render(request, 'adminTemp/login_adm.html', {'login_form': login_form})

@login_required(login_url='login_admin')
def dashboard_adm_view(request):
    if check_admin(request.user):
        adm = Admin.objects.filter(admin_id=request.user.id).first()
        adm_det = Admin.objects.all().filter(status=False)
        eng = Manager.objects.all().filter(status=False)  # get all on-hold managers
        app = Appointment.objects.all().filter(status=False)  # get all on-hold appointments
        cust = Visitor.objects.all()
        
        adm_total = Admin.objects.all().count()  # total visitors
        cust_total = Visitor.objects.all().count()  # total visitors
        eng_total = Manager.objects.all().count()  # get total managers
        app_total = Appointment.objects.all().count()  # get total appointments

        pending_adm_total = Admin.objects.all().filter(status=False).count()  # count onhold admins
        pending_eng_total = Manager.objects.all().filter(status=False).count()  # get total onhold managers
        pending_app_total = Appointment.objects.all().filter(status=False).count()  # get total onhold appointments

        messages.add_message(request, messages.INFO, 'There are {0} appointments that require approval.'.format(pending_app_total))

        context = {'adm': adm, 'eng': eng, 'cust':cust,'app': app, 'adm_det': adm_det,
                   'adm_total': adm_total, 'cust_total': cust_total, 'eng_total': eng_total, 'app_total': app_total,
                   'pending_adm_total': pending_adm_total,
                   'pending_eng_total': pending_eng_total,
                   'pending_app_total': pending_app_total}  # render information

        return render(request, 'adminTemp/dashboard_adm.html', context)
    else:
        auth.logout(request)
        return redirect('login_admin')

@login_required(login_url='login_admin')
def profile_adm_view(request):
    if check_admin(request.user):
        # get information from database
        adm = Admin.objects.filter(admin_id=request.user.id).first()
        if adm is not None:
            dob = adm.dob
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if request.method == "POST":  # profile is updated
                admin_update_form = AdminUpdateForm(request.POST, request.FILES, instance=adm)
                if admin_update_form.is_valid():
                    admin_update_form.save()  # save changes in profile

                    messages.add_message(request, messages.INFO, 'Profile updated successfully!')
                    return redirect('profile_adm.html')
            else:
                admin_update_form = AdminUpdateForm(instance=adm)
            context = {  # render information on webpage
                'admin_update_form': admin_update_form,
                'adm': adm,
                'age': age
            }
            return render(request, 'adminTemp/profile_adm.html', context)
        return render(request, 'login_admin')
    else:
        auth.logout(request)
        return redirect('login_admin')

@login_required(login_url='login_admin')
def book_app_adm_view(request):  # book appointment
    if check_admin(request.user):
        adm = Admin.objects.filter(admin_id=request.user.id).first()
        if request.method == "POST":  # if form is submitted
            app_form = AdminAppointmentForm(request.POST)
            if app_form.is_valid():
                eng_id = app_form.cleaned_data.get('manager')  # get manager id
                cust_id = app_form.cleaned_data.get('visitor')  # get visitor id

                eng = Manager.objects.all().filter(id=eng_id).first()  # get manager
                cust = Visitor.objects.all().filter(id=cust_id).first()  # get visitor

                if check_eng_availability(eng, app_form.cleaned_data.get('app_date'),app_form.cleaned_data.get('app_time')):  # check if appointment is available during that slot
                    app = Appointment(manager=eng, visitor=cust,
                                      description=app_form.cleaned_data.get('description'),
                                      app_date=app_form.cleaned_data.get('app_date'),
                                      app_time=app_form.cleaned_data.get('app_time'),
                                      status=True)  # create new appointment
                    app.save()
                    messages.add_message(request, messages.INFO, 'Appointment created.')
                    return redirect('book_app_admin')
                else:  # if slot is not available, display error
                    messages.add_message(request, messages.INFO, 'Time slot unavailable.')
                    return render(request, 'adminTemp/book_app_adm.html', {'app_form': app_form})
            else:
                messages.add_message(request, messages.INFO, 'Error creating an appointment. Please try again.')
                print(app_form.errors)
        else:
            app_form = AdminAppointmentForm()
        return render(request, 'adminTemp/book_app_adm.html',
                      {'adm': adm, 'app_form': app_form})
    else:
        auth.logout(request)
        return redirect('login_admin')

def dl_report_adm_action(request):
    template_path = 'adminTemp/summary_report.html'

    adm = Admin.objects.filter(admin_id=request.user.id).first()
    adm_det = Admin.objects.all().filter(status=False)
    eng = Manager.objects.all().filter(status=False)  # get all on-hold managers
    app = Appointment.objects.all().filter(status=False)  # get all on-hold appointments

    adm_total = Admin.objects.all().count()  # total visitors
    cust_total = Visitor.objects.all().count()  # total visitors
    eng_total = Manager.objects.all().count()  # get total managers
    app_total = Appointment.objects.all().count()  # get total appointments

    pending_adm_total = Admin.objects.all().filter(status=False).count()  # count onhold admins
    pending_eng_total = Manager.objects.all().filter(status=False).count()  # get total onhold managers
    pending_app_total = Appointment.objects.all().filter(status=False).count()  # get total onhold appointments

    context = {'adm': adm, 'eng': eng,'app': app, 'adm_det': adm_det,
               'adm_total': adm_total, 'cust_total': cust_total, 'eng_total': eng_total, 'app_total': app_total,
               'pending_adm_total': pending_adm_total,
               'pending_eng_total': pending_eng_total,
               'pending_app_total': pending_app_total}

    # context = {'myvar': 'this is your template context'}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Smart Receptionist-summary-report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(html, dest=response)
    # if error then show some funy view
    # if pisa_status.err:
    #     return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

@login_required(login_url='login_admin')
def approve_app_adm_action(request, pk):
    if check_admin(request.user):
        # get information from database
        appointment = Appointment.objects.get(id=pk)
        appointment.status = True  # approve appointment
        appointment.save()

        messages.success(request, "Appointment approved successfully.")
        return redirect(reverse('view_all_app_admin'))
    else:
        auth.logout(request)
        return redirect('login_admin')

# Admin appointment view
@login_required(login_url='login_admin')
def appointment_adm_view(request):
    if check_admin(request.user):
        # get information from database and render in html webpage
        adm = Admin.objects.filter(admin_id=request.user.id).first()
        app = Appointment.objects.all().filter(status=False)
        appointment_app = Appointment.objects.all().filter(status=False).count()
        app_count = Appointment.objects.all().count()
        pending_app_total = Appointment.objects.all().filter(status=False).count()
        approved_app_total = Appointment.objects.all().filter(status=True).count()
        context = {'adm': adm, 'app': app, 'appointment_app': appointment_app, 'app_count': app_count,
                   'pending_app_total': pending_app_total, 'approved_app_total': approved_app_total}
        return render(request, 'adminTemp/appointment_adm.html', context)
    else:
        auth.logout(request)
        return redirect('login_admin')

# All appointments: pending, incomplete, completed
@login_required(login_url='login_admin')
def all_app_adm_view(request):
    if check_admin(request.user):
        adm = Admin.objects.filter(admin_id=request.user.id).first()
        app = Appointment.objects.all().filter(status=False)
        appointment_app = Appointment.objects.all().filter(status=False).count()
        app_count = Appointment.objects.all().count()
        pending_app_total = Appointment.objects.all().filter(status=False).count()
        approved_app_total = Appointment.objects.all().filter(status=True).count()

        appointment_details = []
        for app in Appointment.objects.filter(status=True).all():  # get approved appointments
            e = app.manager
            c = app.visitor
            if e and c:
                appointment_details.append([e.first_name, e.last_name, e.role,
                                            c.first_name, c.last_name, 
                                            app.description, app.appointment_date, app.appointment_time,
                                            app.pk, app.completed, app.status])  # render information

        pending_appointment_details = []
        for app in Appointment.objects.filter(status=False).all():  # get pending appointments
            e = app.manager
            c = app.visitor
            if e and c:
                pending_appointment_details.append([e.first_name, e.last_name, e.role,
                                                    c.first_name, c.last_name, 
                                                    app.description, app.appointment_date, app.appointment_time,
                                                    app.pk, app.completed, app.status])  # render information on webpage

        return render(request, 'adminTemp/view_all_app_adm.html',
                      {'adm': adm, 'app': app, 'appointment_app': appointment_app, 'app_count': app_count,
                       'pending_app_total': pending_app_total, 'approved_app_total': approved_app_total,
                       'appointment_details': appointment_details,
                       'pending_appointment_details': pending_appointment_details})
    else:
        auth.logout(request)
        return redirect('login_admin')

# Approved appointment's details
@login_required(login_url='login_admin')
def app_details_adm_view(request, pk):
    if check_admin(request.user):
        adm = Admin.objects.filter(admin_id=request.user.id).first()
        app = Appointment.objects.filter(id=pk).first()  # get appointment
        if app is not None:
            eng = app.manager
            cust = app.visitor


            appointment_details = [eng.first_name, eng.last_name,
                                cust.first_name, cust.last_name,
                                cust.postcode, cust.city, cust.country,
                                app.appointment_date, app.appointment_time, app.description,
                                app.status, app.completed, pk]  # render fields

            return render(request, 'adminTemp/view_app_details_adm.html',
                        {'adm': adm,
                        'eng': eng,
                        'app': app,
                        'cust': cust,
                        'appointment_details': appointment_details})
        return render(request, 'appointment_admin')
    else:
        auth.logout(request)
        return redirect('login_admin')

@login_required(login_url='login_admin')
def complete_app_adm_action(request, pk):
    if check_admin(request.user):
        # get information from database and render in html webpage
        app = Appointment.objects.get(id=pk)
        app.completed = True
        app.save()

        messages.add_message(request, messages.INFO, 'Appointment completed successfully!')
        return redirect('view_all_app_admin')
    else:
        auth.logout(request)
        return redirect('login_admin')


# Visitor section
@login_required(login_url='login_admin')
def visitor_adm_view(request):
    if check_admin(request.user):
        # get information from database and render in html webpage
        adm = Admin.objects.filter(admin_id=request.user.id).first()
        cust = Visitor.objects.all()
        cust_count = Visitor.objects.all().count()
        context = {'adm': adm, 'cust': cust,
                   'cust_count': cust_count}
        return render(request, 'adminTemp/visitor_adm.html', context)
    else:
        auth.logout(request)
        return redirect('login_admin')

#Feedback section
def feedback_adm_view(request):
    if check_admin(request.user):
        # get information from database and render in html webpage
        feedback = Feedback.objects.all()
        feedback_count = Visitor.objects.all().count()
        context = {'cust': feedback,
                   'cust_count': feedback_count}
        return render(request, 'adminTemp/feedbacks.html', context)
    else:
        auth.logout(request)
        return redirect('login_admin')

# Manager section
@login_required(login_url='login_admin')
def manager_adm_view(request):  # view managers
    if check_admin(request.user):
        # get information from database and render in html webpage
        adm = Admin.objects.filter(admin_id=request.user.id).first()
        eng = Manager.objects.all().filter(status=False)
        eng_approved = Manager.objects.all().filter(status=True).count()
        eng_pending = Manager.objects.all().filter(status=False).count()
        eng_count = Manager.objects.all().count()
        context = {'adm': adm, 'eng': eng, 'eng_approved': eng_approved, 'eng_pending': eng_pending,
                   'eng_count': eng_count}
        return render(request, 'adminTemp/manager_adm.html', context)
    else:
        auth.logout(request)
        return redirect('login_admin')


# Approve manager account
@login_required(login_url='login_admin')
def approve_mgr_adm_view(request):
    if check_admin(request.user):
        # get information from database and render in html webpage
        adm = Admin.objects.filter(admin_id=request.user.id).first()
        eng = Manager.objects.all().filter(status=False)
        eng_approved = Manager.objects.all().filter(status=True).count()
        eng_pending = Manager.objects.all().filter(status=False).count()
        eng_count = Manager.objects.all().count()
        context = {'adm': adm, 'eng': eng, 'eng_approved': eng_approved, 'eng_pending': eng_pending,
                   'eng_count': eng_count}
        return render(request, 'adminTemp/approve_mgr.html', context)
    else:
        auth.logout(request)
        return redirect('login_admin')


# Approve manager action
@login_required(login_url='login_admin')
def approve_mgr_adm_action(request, pk):
    if check_admin(request.user):
        # get information from database
        eng = Manager.objects.get(id=pk)
        eng.status = True  # approve manager
        eng.save()

        messages.add_message(request, messages.INFO, 'manager approved successfully.')
        return redirect(reverse('approve_manager'))
    else:
        auth.logout(request)
        return redirect('login_admin')


# View all managers
@login_required(login_url='login_admin')
def all_mgr_adm_view(request):
    # get information from database and render in html webpage
    if check_admin(request.user):
        adm = Admin.objects.filter(admin_id=request.user.id).first()
        eng = Manager.objects.all().filter(status=False)
        eng_approved = Manager.objects.all().filter(status=True).count()
        eng_pending = Manager.objects.all().filter(status=False).count()
        eng_count = Manager.objects.all().count()

        eng_details = []
        for e in Manager.objects.filter(status=True).all():
            eng_details.append(
                [e.pk, e.image.url, e.first_name, e.last_name, e.dob, e.address, e.postcode, e.city, e.country,
                 e.role, e.status])

        context = {'adm': adm, 'eng': eng, 'eng_approved': eng_approved, 'eng_pending': eng_pending,
                   'eng_count': eng_count, 'eng_details': eng_details}

        return render(request, 'adminTemp/view_all_mgr.html', context)
    else:
        auth.logout(request)
        return redirect('login_admin')


#VISITOR
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
                subject_choice = feedback_form.cleaned_data['Subject']  # get message from form
                
                message = feedback_form.cleaned_data['Message']  # get message from form

                fdb = Feedback(email = email,name=name, subject = subject_choice,message = message) 
                fdb.save()
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

#MANAGER
@login_required(login_url = 'login_manager')
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
        return redirect('login_manager')

def login_mgr_view(request):  # login manager
    if request.method == "POST":
        login_form = AuthenticationForm(request=request, data=request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            user = auth.authenticate(username=username, password=password)
            if user is not None and check_manager(user):
                auth.login(request, user)
                account_approval = Manager.objects.all().filter(status=True, manager=request.user.id)
                if account_approval:
                    return redirect('profile_manager')
                else:
                    messages.add_message(request, messages.INFO, 'Your account is currently pending. '
                                                                 'Please wait for approval.')
                    return render(request, 'manager/login_mgr.html', {'login_form': login_form})
        return render(request, 'manager/login_mgr.html', {'login_form': login_form})
    else:
        login_form = AuthenticationForm()
    return render(request, 'manager/login_mgr.html', {'login_form': login_form})

@login_required(login_url = 'login_manager')
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

@login_required(login_url = 'login_manager')
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

@login_required(login_url = 'login_manager')
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
        return redirect('login_admin')

@login_required(login_url = 'login_manager')
def complete_app_eng_action(request, pk):
    if check_manager(request.user):
        # get information from database and render in html webpage
        app = Appointment.objects.get(id=pk)
        app.completed = True
        app.save()

        messages.add_message(request, messages.INFO, 'Appointment completed successfully!')
        return redirect('view_app_mgr.html')
    else:
        auth.logout(request)
        return redirect('login_eng.html')


@login_required(login_url = 'login_manager')
def get_link_mgr_action(request, pk):
    if check_manager(request.user):
        # get information from database
        appointment = Appointment.objects.get(id=pk)
        appointment.status = True  # approve appointment
        appointment.save()

        eng = appointment.manager
        esf = ManagerAppointments.objects.filter(manager=eng).first()
        if esf is not None:
            esf.app_total += 1  # add visitor to manager count
            esf.save()

        messages.add_message(request, messages.INFO, 'Appointment approved!')
        return redirect(reverse('manager_appointments'))
    else:
        auth.logout(request)
        return redirect('login_eng.html')

@login_required(login_url = 'login_manager')
def approved_app_eng_view(request):
    if check_manager(request.user):
        eng = Manager.objects.get(manager=request.user.id)  # get manager

        incomplete_appointments = []
        for aca in ApprovedVisitorAppointment.objects.filter(
                manager=eng).all():  # get all visitors approved under this manager
            cust = aca.visitor
            if cust and not aca.completed_date:
                incomplete_appointments.append([eng.first_name, cust.first_name,
                                                aca.approval_date, aca.completed_date, aca.pk])

        completed_appointments = []
        for aca in ApprovedVisitorAppointment.objects.filter(
                manager=eng).all():  # get all visitors approved under this manager
            cust = aca.visitor
            if cust and aca.completed_date:
                completed_appointments.append([eng.first_name, cust.first_name,
                                               aca.approval_date, aca.completed_date, aca.pk])
        return render(request, 'manager/view_approved_app_eng.html',
                      {'incomplete_appointments': incomplete_appointments,
                       'completed_appointments': completed_appointments})
    else:
        auth.logout(request)
        return redirect('login_eng.html')

@login_required(login_url = 'login_manager')
def feedback_manager_view(request):
    if check_manager(request.user):
        eng = Manager.objects.get(manager=request.user.id)
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
                    .format(
                    dict(feedback_form.subject_choices).get(feedback_form.cleaned_data['Subject']),
                    datetime.datetime.now(),
                    feedback_form.cleaned_data['Message']
                )

                try:
                    mail_admins(subject, message)
                    messages.add_message(request, messages.INFO, 'Thank you for submitting your feedback.')

                    return redirect('feedback_eng.html')
                except:
                    feedback_form.add_error('Email',
                                            'Try again.')
                    return render(request, 'manager/feedback_mgr.html', {'feedback_form': feedback_form})
        return render(request, 'manager/feedback_mgr.html', {'eng': eng, 'feedback_form': feedback_form})
    else:
        auth.logout(request)
        return redirect('login_eng.html')

@login_required(login_url = 'login_manager')
def book_app_manager_view(request):
    if check_manager(request.user):
        vis = Manager.objects.filter(manager=request.user.id).first()
        app_details = []

        for app in Appointment.objects.filter(manager=vis, status=False).all():
            e = app.visitor
            if e:
                app_details.append([e.first_name, e.last_name,
                                    app.description, app.appointment_date, app.appointment_time, app.status])

        if request.method == "POST":  # if visitor books an appointment
            app_form = ManagerAppointmentForm(request.POST)

            if app_form.is_valid():  # if form is valid
                eng_id = int(app_form.cleaned_data.get('visitor'))  # get manager id from form
                eng = Visitor.objects.all().filter(id=eng_id).first()  # get manager from form

                if check_mgr_availability(eng,  # check if manager is available during that slot
                                          app_form.cleaned_data.get('app_date'),
                                          app_form.cleaned_data.get('app_time')):
                    app_date = app_form.cleaned_data.get('app_date')  # get appointment date
                    if timezone.now().date() < app_date:  # check if appointment date is valid
                        app = Appointment(manager=vis,
                                          visitor=eng,
                                          description=app_form.cleaned_data.get('description'),
                                          appointment_date=app_form.cleaned_data.get('app_date'),
                                          appointment_time=app_form.cleaned_data.get('app_time'),
                                          status=False)  # create appointment instance, which is unapproved
                        app.save()
                        messages.add_message(request, messages.INFO, 'Your appointment is received and pending.')
                        return redirect('book_app_manager')
                    else:
                        app_form.add_error('app_date', 'Invalid date.')
                else:  # if manager is busy
                    app_form.add_error('app_time', 'Slot Unavailable.')
                return render(request, 'manager/book_app_mgr.html',
                              {'app_form': app_form, 'app_details': app_details})
            else:  # if form is invalid
                print(app_form.errors)
        else:
            app_form = ManagerAppointmentForm()
        return render(request, 'manager/book_app_mgr.html',
                      {'vis': vis, 'app_form': app_form, 'app_details': app_details})
    else:
        auth.logout(request)
        return redirect('login_vis.html')

@login_required(login_url = 'login_manager')
def completed_app_managers_view(request):
    if check_manager(request.user):
        # get information from database and render in html webpage
        vis = Manager.objects.filter(manager=request.user.id).first()

        total_app = Appointment.objects.filter(manager=vis).count()
        total_approved_app = Appointment.objects.filter(status=True, manager=vis).count()
        total_pending_app = Appointment.objects.filter(status=False, manager=vis).count()
        # app_total = Appointment.objects.filter(status=True, visitor=vis).all()

        completed_appointment_details = []
        for app in Appointment.objects.filter(status=True, completed=True,
                                              manager=vis).all():  # get all approved appointments
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

        return render(request, 'manager/completed_app_manager.html',
                      context)
    else:
        auth.logout(request)
        return redirect('login_vis.html')














# User check
def check_admin(user):  # check if user is admin
    return user.groups.filter(name='Admin').exists()

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

def check_mgr_availability(visitor, dt, tm):  # check if manager is available in a given slot
    hour, minute = tm.split(':')
    ftm = time(int(hour), int(minute), 0)
    app = Appointment.objects.all().filter(status=True,
                                           visitor=visitor,
                                           appointment_date=dt)  # get all appointments for a given eng and the given date

    if ftm < time(9, 0, 0) or ftm > time(17, 0, 0):  # if time is not in between 9AM to 5PM, reject
        return False

    if time(12, 0, 0) < ftm < time(13, 0, 0):  # if time is in between 12PM to 1PM, reject
        return False

    for a in app:
        if ftm == a.appointment_time and dt == a.appointment_date:  # if some other appointment has the same slot, reject
            return False

    return True


def contact_us(request):
    if check_visitor(request.user):    
        return render(request, 'visitor/contact.html', {'log_user':'visitor'})
    
    if check_manager(request.user):    
        return render(request, 'visitor/contact.html', {'log_user':'manager'})
    if check_admin(request.user):    
        return render(request, 'visitor/contact.html', {'log_user':'admin'})
    
    return redirect('/')

def index(request):
    user = request.user
    if check_visitor(request.user):    
        return redirect('/visitor/profile')
    if check_manager(request.user):    
        return redirect('/manager/profile')
    return redirect('/')

def home(request):
    return render(request, 'index.html')