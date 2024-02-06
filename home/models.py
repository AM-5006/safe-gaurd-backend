from django.db import models

from django.contrib.auth.models import User
# Create your models here.

class Camera(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    source = models.TextField(blank=True, null=True)

    rtsp_status = models.BooleanField(default=False)
    rtsp_message = models.CharField(max_length=255, blank=True, null=True)
    rtsp_frame = models.ImageField(upload_to='status/', default='default.jpeg', null=True, blank=True)

    helmet = models.BooleanField(default=False)
    vest = models.BooleanField(default=False)
    
    polygons = models.TextField(blank=True, null=True)
    email_alert = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.id}-{self.location}"

    class Meta:
        verbose_name = 'Camera'
        verbose_name_plural = 'Cameras'

class Employee(models.Model):
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=10, blank=True, null=True)
    
    def __str__(self):
        return f"{self.id}-{self.first_name}"

    class Meta:
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'

class Incident(models.Model):
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    employee = models.ManyToManyField(Employee, blank=True)
    incident = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(null=True, blank=True)
    incident_image = models.ImageField(upload_to='images/incident/', default='default.png')

    def __str__(self):
        return f"{self.camera.id}-{self.timestamp}"
    
    class Meta:
        verbose_name = 'IncidentLog'
        verbose_name_plural = 'IncidentLogs'

