from django.contrib import admin
from .models import UserProfile, Visitor, Manager

admin.site.register(UserProfile)
admin.site.register(Visitor)
admin.site.register(Manager)
