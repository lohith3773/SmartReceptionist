from django import forms
from .models import Appointment, Admin
from django.forms.widgets import SelectDateWidget
from FaceRecognition.models import Manager, Visitor
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# Admin registration form
class AdminRegistrationForm(UserCreationForm):  # to register an admin
    username = forms.CharField(required=True, label="", widget=forms.TextInput(attrs={'placeholder': 'Enter your username'}))
    username.widget.attrs.update({'class': 'app-form-control'})

    email = forms.EmailField(required=True, label="", widget=forms.TextInput(attrs={'placeholder': 'Enter your email'}))
    email.widget.attrs.update({'class': 'app-form-control'})

    first_name = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'Enter your first name'}))
    first_name.widget.attrs.update({'class': 'app-form-control'})

    last_name = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'Enter your last name'}))
    last_name.widget.attrs.update({'class': 'app-form-control'})

    dob = forms.DateField(label="", widget=SelectDateWidget(years=range(1960, 2021)))
    dob.widget.attrs.update({'class': 'app-form-control-date'})

    address = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'Enter your address'}))
    address.widget.attrs.update({'class': 'app-form-control'})

    city = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'City'}))
    city.widget.attrs.update({'class': 'app-form-control'})

    country = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'Country'}))
    country.widget.attrs.update({'class': 'app-form-control'})

    postcode = forms.IntegerField(label="", widget=forms.TextInput(attrs={'placeholder': 'Postcode'}))
    postcode.widget.attrs.update({'class': 'app-form-control'})

    password1 = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    password1.widget.attrs.update({'class': 'app-form-control'})

    password2 = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password again'}))
    password2.widget.attrs.update({'class': 'app-form-control'})

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'dob', 'address', 'city', 'country', 'postcode',
                 'password1', 'password2']
        help_texts = {k: "" for k in fields}


# Admin details update form
class AdminUpdateForm(forms.ModelForm):  # used to edit an admin instance
    first_name = forms.CharField()
    last_name = forms.CharField()
    dob = forms.DateField(widget=SelectDateWidget(years=range(1960, 2022)))
    address = forms.CharField()
    city = forms.CharField()
    country = forms.CharField()
    postcode = forms.IntegerField()

    class Meta:
        model = Admin
        fields = ['first_name', 'last_name', 'dob', 'address', 'city', 'country', 'postcode']


# Admin appointment form
class AdminAppointmentForm(forms.ModelForm):  # book an appointment by admin
    manager = forms.TypedChoiceField(label='')  # engineer is chosen from existing engineers in db
    manager.widget.attrs.update({'class': 'app-form-control'})
    visitor = forms.TypedChoiceField(label='')  # customer is chosen from existing customers in db
    visitor.widget.attrs.update({'class': 'app-form-control'})
    app_date = forms.DateField(label='', widget=SelectDateWidget(years=range(2022, 2024)))  # appointment date
    app_date.widget.attrs.update({'class': 'app-form-control-date'})
    app_time = forms.TypedChoiceField(label='')  # time of appointment
    app_time.widget.attrs.update({'class': 'app-form-control'})
    description = forms.CharField(max_length=300, label='',
                                  widget=forms.TextInput(attrs={'placeholder': 'Description'}))
    description.widget.attrs.update({'class': 'app-form-control'})

    def __init__(self, *args, **kwargs):
        super(AdminAppointmentForm, self).__init__(*args, **kwargs)
        self.fields['manager'].choices = [(c.pk, c.first_name + " " + c.last_name + " (" + c.role + ")")
                                           for c in Manager.objects.filter(status=True).all()]
        # choose engineers from db
        self.fields['visitor'].choices = [(c.pk, c.first_name + " " + c.last_name)
                                           for c in Visitor.objects.all()]
        # choose customers from db
        self.fields['app_time'].choices = [('9:00', '9:00'), ('10:00', '10:00'), ('11:00', '11:00'),
                                           ('13:00', '13:00'), ('14:00', '14:00'), ('15:00', '15:00'),
                                           ('16:00', '16:00'), ('17:00', '17:00')]
        # choices for time slot for appointment

    class Meta:
        model = Appointment
        fields = ['description', 'app_date', 'app_time']



class VisitorAppointmentForm(forms.ModelForm):  # make an appointment by customer
    manager = forms.TypedChoiceField(label='')  # choose engineer from db
    manager.widget.attrs.update({'class': 'app-form-control'})
    # eng_id=forms.CharField(widget=forms.Select(choices=c))
    app_date = forms.DateField(label='', widget=SelectDateWidget(years=range(2022, 2024)))  # date of appointment
    app_date.widget.attrs.update({'class': 'app-form-control-date'})
    app_time = forms.TypedChoiceField(label='')  # time of appointment
    app_time.widget.attrs.update({'class': 'app-form-control'})
    description = forms.CharField(max_length=300, label='',
                                  widget=forms.TextInput(attrs={'placeholder': 'Description'}))
    description.widget.attrs.update({'class': 'app-form-control'})

    def __init__(self, *args, **kwargs):
        super(VisitorAppointmentForm, self).__init__(*args, **kwargs)
        self.fields['manager'].choices = [(e.pk, e.first_name + " " + e.last_name + e.role )
                                           for e in Manager.objects.all()]
        # choose engineers from db
        self.fields['app_time'].choices = [('9:00', '9:00'), ('10:00', '10:00'), ('11:00', '11:00'),
                                           ('13:00', '13:00'), ('14:00', '14:00'), ('15:00', '15:00'),
                                           ('16:00', '16:00'), ('17:00', '17:00')]
        # choices for time slot for appointment

    class Meta:
        model = Appointment
        fields = ['description', 'app_date', 'app_time']

class ManagerAppointmentForm(forms.ModelForm):  # make an appointment by customer
    visitor = forms.TypedChoiceField(label='')  # choose engineer from db
    visitor.widget.attrs.update({'class': 'app-form-control'})
    # eng_id=forms.CharField(widget=forms.Select(choices=c))
    app_date = forms.DateField(label='', widget=SelectDateWidget(years=range(2022, 2024)))  # date of appointment
    app_date.widget.attrs.update({'class': 'app-form-control-date'})
    app_time = forms.TypedChoiceField(label='')  # time of appointment
    app_time.widget.attrs.update({'class': 'app-form-control'})
    description = forms.CharField(max_length=300, label='',
                                  widget=forms.TextInput(attrs={'placeholder': 'Description'}))
    description.widget.attrs.update({'class': 'app-form-control'})

    def __init__(self, *args, **kwargs):
        super(ManagerAppointmentForm, self).__init__(*args, **kwargs)
        self.fields['visitor'].choices = [(e.pk, e.first_name + " " + e.last_name )
                                           for e in Visitor.objects.all()]
        # choose engineers from db
        self.fields['app_time'].choices = [('9:00', '9:00'), ('10:00', '10:00'), ('11:00', '11:00'),
                                           ('13:00', '13:00'), ('14:00', '14:00'), ('15:00', '15:00'),
                                           ('16:00', '16:00'), ('17:00', '17:00')]
        # choices for time slot for appointment

    class Meta:
        model = Appointment
        fields = ['description', 'app_date', 'app_time']

