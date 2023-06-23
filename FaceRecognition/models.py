from django.db import models
from django.contrib.auth.models import User
import datetime
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
 
def default_user():  
    user = User(username="deleteduser", email="deleteduser@deleted.com")
    return user.pk
   
class Visitor(models.Model):
    visitor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Visitor')
    image = models.ImageField(default="default.png",upload_to='profile_pictures',null=True, blank=True)
    first_name = models.CharField(max_length=100, default='first_name')  
    last_name = models.CharField(max_length=100, default='last_name') 
    dob = models.DateField(default=datetime.date.today)
    address = models.CharField(max_length=300, default="address")  
    email_address = models.CharField(max_length=100,default='email')
    city = models.CharField(max_length=100, default="city")  
    postcode = models.IntegerField(default=0)  # customer postcode
    country = models.CharField(max_length=100, default="country")
    
    def __str__(self):
       return f'{self.visitor.username} Visitor Profile'
   
class Manager(models.Model):
    manager = models.ForeignKey(User, on_delete=models.CASCADE,related_name='Manager')
    image = models.ImageField(default="default.png",upload_to='profile_pictures',null=True, blank=True)
    first_name = models.CharField(max_length=100, default='first_name')  
    last_name = models.CharField(max_length=100, default='last_name') 
    role = models.CharField(max_length=100,default='role')
    dob = models.DateField(default=datetime.date.today)
    address = models.CharField(max_length=300, default="address")  
    email_address = models.CharField(max_length=100,default='email')
    city = models.CharField(max_length=100, default="city")  
    postcode = models.IntegerField(default=0)  
    country = models.CharField(max_length=100, default="country")
    status = models.BooleanField(default=False)  # engineer status(approved/on-hold)
    def __str__(self):
       return f'{self.manager.username} Manager Profile'

class ManagerAppointments(models.Model):
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE, related_name="EngineerServiceField")  # engineer fk
    app_total = models.IntegerField(default=0)  # total customers/appointments completed by engineer

    def __str__(self):
        return f'{self.manager.first_name} appointments Information'

class Analytics(models.Model):
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, related_name="VisitorAnalytics")  
    check_in_time = models.DateTimeField(auto_now_add=True)