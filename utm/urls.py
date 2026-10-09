"""
URL configuration for utm project.

Unified Telemetry Monitor (UTM) - Drone Tracking System.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Root redirects to main dashboard
    path('', RedirectView.as_view(url='/login/', permanent=False), name='root'),
    # Include all telemetry dashboard & API routes
    path('', include('telemetry.urls')),
]
