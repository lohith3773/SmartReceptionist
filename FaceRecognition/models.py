from django.db import models

class User(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    face_image = models.ImageField(upload_to='faces/')

    def __str__(self):
        return self.username
class Visitors(models.Model):
    Visitor_id = models.CharField(max_length=100)
    Visitor_Name = models.CharField(max_length=100)
