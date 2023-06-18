from django.db import models
from django.contrib.auth.models import User
import datetime
from django.core.validators import MaxValueValidator, MinValueValidator

from FaceRecognition.models import Visitor, Manager

subject_choices = [
        ('APPOINTMENT', 'Appointment'),
        ('FEEDBACK', 'Feedback'),
        ('NEW_FEATURE', 'Feature Request'),
        ('BUG', 'Bug'),
        ('OTHER', 'Other'),
    ]

class Appointment(models.Model):  
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, related_name="VisitorApp")  
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE, related_name="ManagerApp")  
    description = models.TextField(max_length=500)  
    appointment_date = models.DateField(null=True, blank=True) 
    appointment_time = models.TimeField(null=True, blank=True) 
    status = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.description} Appointment Information'
    
class AppointmentRating(models.Model):
    rating = models.IntegerField(default=0,
                                 validators=[
                                     MaxValueValidator(5),
                                     MinValueValidator(0)])

    def __str__(self):
        return f'{self.rating} Stars - Appointment Rating Information'
    
class ApprovedVisitorAppointment(models.Model):
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, related_name="VisitorApprovedApp")  
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE, related_name="ManagerApprovedApp")   
    approval_date = models.DateField()  # date appointment approved
    description = models.TextField()  # appointment description
    completed_date = models.DateField(null=True, blank=True)  # date of completed appointment

    def __str__(self):
        return f'{self.visitor} Approved Appointment Information'
    
    class Meta:
        unique_together = ('visitor', 'manager', 'approval_date')
        
class Admin(models.Model):  # Admin details
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Admin")  # user foreign key
    first_name = models.CharField(max_length=100, default='first_name')  # admin first name
    last_name = models.CharField(max_length=100, default='last_name')  # admin lastname
    dob = models.DateField(default=datetime.date.today)  # date of birth
    address = models.CharField(max_length=300, default="address")  # admin address
    city = models.CharField(max_length=100, default="city")  # admin city
    country = models.CharField(max_length=100, default="country")  # admin country
    postcode = models.IntegerField(default=0)  # admin postcode
    status = models.BooleanField(default=False)  # admin status (approved/on-hold)

    def __str__(self):
        return f'{self.admin.username} Admin Profile'

class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    subject = models.CharField(max_length=50,choices=subject_choices,default="Appointment")
    message = models.CharField(max_length=255)