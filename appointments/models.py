from django.db import models
from django.contrib.auth.models import User
import datetime
from django.core.validators import MaxValueValidator, MinValueValidator

from FaceRecognition.models import Visitor, Manager



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