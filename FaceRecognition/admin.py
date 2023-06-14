from django.contrib import admin
from .models import UserProfile, Visitor, Manager, ManagerAppointments

admin.site.register(UserProfile)
admin.site.register(Visitor)
admin.site.register(Manager)
admin.site.register(ManagerAppointments)

