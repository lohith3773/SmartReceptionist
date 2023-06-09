from django import forms
from .models import Appointment
from django.forms.widgets import SelectDateWidget
from FaceRecognition.models import Manager

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

