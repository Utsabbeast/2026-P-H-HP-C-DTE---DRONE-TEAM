import sys
import os

models_code = """
from django.contrib.auth.models import User

class PilotProfile(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pilot_profile')
    license_number = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pilot Profile'
        verbose_name_plural = 'Pilot Profiles'

    def __str__(self):
        return f"{self.user.username} - {self.get_status_display()}"

class DroneRegistration(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
    CATEGORY_CHOICES = (
        ('NANO', 'Nano (<= 250g)'),
        ('MICRO', 'Micro (> 250g to <= 2kg)'),
        ('SMALL', 'Small (> 2kg to <= 25kg)'),
        ('MEDIUM', 'Medium (> 25kg to <= 150kg)'),
        ('LARGE', 'Large (> 150kg)'),
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='drones')
    name = models.CharField(max_length=255)
    uin = models.CharField(max_length=50, unique=True, blank=True, null=True, help_text="Unique Identification Number")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='MICRO')
    max_altitude_m = models.FloatField(default=120.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Drone Registration'
        verbose_name_plural = 'Drone Registrations'

    def __str__(self):
        return f"{self.name} ({self.uin}) - {self.owner.username}"
"""

with open('telemetry/models.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'PilotProfile' not in content:
    with open('telemetry/models.py', 'a', encoding='utf-8') as f:
        f.write(models_code)

admin_code = """
from .models import PilotProfile, DroneRegistration

@admin.register(PilotProfile)
class PilotProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number', 'status', 'created_at')
    list_filter = ('status',)

@admin.register(DroneRegistration)
class DroneRegistrationAdmin(admin.ModelAdmin):
    list_display = ('name', 'uin', 'owner', 'category', 'status', 'created_at')
    list_filter = ('status', 'category')
"""

with open('telemetry/admin.py', 'r', encoding='utf-8') as f:
    admin_content = f.read()

if 'PilotProfile' not in admin_content:
    with open('telemetry/admin.py', 'a', encoding='utf-8') as f:
        f.write(admin_code)

print("Added models and admin logic")
