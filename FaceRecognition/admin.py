from django.contrib import admin
from .models import UserProfile, Visitor, Manager, ManagerAppointments, Analytics

admin.site.register(UserProfile)
admin.site.register(Visitor)
admin.site.register(Manager)
admin.site.register(ManagerAppointments)
admin.site.register(Analytics)

