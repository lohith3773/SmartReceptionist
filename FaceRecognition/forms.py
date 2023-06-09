from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms.widgets import SelectDateWidget
from django.contrib.auth.models import User
from .models import Visitor, Manager
from django.utils import timezone


class RegistrationForm(UserCreationForm):
    name = forms.CharField(max_length=30, required=True)
    class Meta:
        model = User
        fields = ('username', 'name', 'password1', 'password2')

class VisitorRegistrationForm(UserCreationForm):  
    username = forms.CharField(required=True, label="", widget=forms.TextInput(attrs={'placeholder': 'Enter your username'}))
    username.widget.attrs.update({'class': 'app-form-control'})

    email_address = forms.EmailField(required=True, label="", widget=forms.TextInput(attrs={'placeholder': 'Enter your email'}))
    email_address.widget.attrs.update({'class': 'app-form-control'})

    first_name = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'Enter your first name'}))
    first_name.widget.attrs.update({'class': 'app-form-control'})

    last_name = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'Enter your last name'}))
    last_name.widget.attrs.update({'class': 'app-form-control'})

    dob = forms.DateField(label="", widget=SelectDateWidget(years=range(1960, 2022)))
    dob.widget.attrs.update({'class': 'app-form-control-date'})

    address = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'Enter your address'}))
    address.widget.attrs.update({'class': 'app-form-control'})

    city = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'City'}))
    city.widget.attrs.update({'class': 'app-form-control'})

    postcode = forms.IntegerField(label="", widget=forms.TextInput(attrs={'placeholder': 'Postcode'}))
    postcode.widget.attrs.update({'class': 'app-form-control'})

    country = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'Country'}))
    country.widget.attrs.update({'class': 'app-form-control'})

    image = forms.ImageField(label="")
    image.widget.attrs.update({'class': 'app-form-control'})

    password1 = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    password1.widget.attrs.update({'class': 'app-form-control'})

    password2 = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password again'}))
    password2.widget.attrs.update({'class': 'app-form-control'})

    class Meta:
        model = User
        fields = ['username', 'email_address', 'first_name', 'last_name', 'dob',
                  'city', 'country', 'postcode', 'image', 'password1', 'password2']
        help_texts = {k: "" for k in fields}

class VisitorUpdateForm(forms.ModelForm):  
    first_name = forms.CharField()
    last_name = forms.CharField()
    dob = forms.DateField(widget=SelectDateWidget(years=range(1960, 2022)))
    city = forms.CharField()
    country = forms.CharField()
    image = forms.ImageField(widget=forms.FileInput)
    postcode = forms.IntegerField()

    class Meta:
        model = Visitor
        fields = ['first_name', 'last_name', 'dob', 'city', 'country', 'postcode','image']


class ManagerRegistrationForm(UserCreationForm):  # register manager
    username = forms.CharField(required=True, label="", widget=forms.TextInput(attrs={'placeholder': 'Enter your username'}))
    username.widget.attrs.update({'class': 'app-form-control'})

    email = forms.EmailField(required=True, label="", widget=forms.TextInput(attrs={'placeholder': 'Enter your email'}))
    email.widget.attrs.update({'class': 'app-form-control'})

    first_name = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'Enter your first name'}))
    first_name.widget.attrs.update({'class': 'app-form-control'})

    last_name = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'Enter your last name'}))
    last_name.widget.attrs.update({'class': 'app-form-control'})

    role = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'Enter your Role'}))
    role.widget.attrs.update({'class': 'app-form-control'})

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

    image = forms.ImageField(label="")
    image.widget.attrs.update({'class': 'app-form-control'})

    password1 = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    password1.widget.attrs.update({'class': 'app-form-control'})

    password2 = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password again'}))
    password2.widget.attrs.update({'class': 'app-form-control'})

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'dob', 'address', 'city', 'country',
                  'postcode', 'image', 'password1', 'password2']
        help_texts = {k: "" for k in fields}

    def check_date(self):  # form date of birth validator
        cleaned_data = self.cleaned_data
        dob = cleaned_data.get('dob')
        if dob < timezone.now().date():
            return True
        self.add_error('dob', 'Invalid date of birth.')
        return False

class ManagerUpdateForm(forms.ModelForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    dob = forms.DateField(widget=SelectDateWidget(years=range(1960, 2022)))
    address = forms.CharField()
    city = forms.CharField()
    country = forms.CharField()
    postcode = forms.IntegerField()
    image = forms.ImageField(widget=forms.FileInput)

    class Meta:
        model = Manager
        fields = ['first_name', 'last_name', 'dob', 'address', 'city', 'country', 'postcode', 'image']

class FeedbackForm(forms.Form):  # contact us form (feedback), used by customers/managers to send feedbacks using mail to admins
    APPOINTMENT = 'app'
    BUG = 'b'
    FEEDBACK = 'fb'
    NEW_FEATURE = 'nf'
    OTHER = 'o'
    subject_choices = (
        (APPOINTMENT, 'Appointment'),
        (FEEDBACK, 'Feedback'),
        (NEW_FEATURE, 'Feature Request'),
        (BUG, 'Bug'),
        (OTHER, 'Other'),
    )

    Name = forms.CharField(max_length=30, label="", widget=forms.TextInput(attrs={'placeholder': 'Enter your name'}))
    Name.widget.attrs.update({'class': 'form-control'})
    Email = forms.EmailField(label="", widget=forms.TextInput(attrs={'placeholder': 'example@email.com'}))
    Email.widget.attrs.update({'class': 'form-control'})
    Subject = forms.ChoiceField(label='', choices=subject_choices)
    Subject.widget.attrs.update({'class': 'form-control'})
    Message = forms.CharField(max_length=500, label="", widget=forms.TextInput(attrs={'placeholder': 'Enter your message here'}))
    Message.widget.attrs.update({'class': 'form-control'})