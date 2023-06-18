from django.contrib import admin
from .models import Appointment,Admin, Feedback
# Register your models here.
admin.site.register(Appointment)
admin.site.register(Admin)
admin.site.register(Feedback)
