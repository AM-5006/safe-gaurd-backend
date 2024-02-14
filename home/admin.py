from django.contrib import admin

from .models import *
# Register your models here.

class CameraAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'location')

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('emp_id', 'first_name', 'last_name')

class IncidentAdmin(admin.ModelAdmin):
    list_display = ('id', 'camera', 'timestamp')

admin.site.register(Camera, CameraAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Incident, IncidentAdmin)