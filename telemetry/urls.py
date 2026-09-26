from django.urls import path
from . import views

app_name = 'telemetry'

urlpatterns = [
    # Dashboard views
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('mobile/', views.MobilePageView.as_view(), name='mobile'),

    # Phone GPS Test Mode APIs
    path('api/phone-location/', views.PhoneLocationIngestView.as_view(), name='phone-location-ingest'),
    path('api/phone-location/latest/', views.PhoneLocationLatestView.as_view(), name='phone-location-latest'),
    path('api/phone-location/history/', views.PhoneLocationHistoryView.as_view(), name='phone-location-history'),

    # Core ESP32 & UTM Drone Telemetry APIs (Preserved for future hardware integration)
    path('api/telemetry/', views.TelemetryIngestView.as_view(), name='telemetry-ingest'),
    path('api/telemetry/latest/', views.TelemetryLatestView.as_view(), name='telemetry-latest'),
    path('api/telemetry/history/', views.TelemetryHistoryView.as_view(), name='telemetry-history'),
    path('api/telemetry/status/', views.DroneStatusView.as_view(), name='drone-status'),

    # Simulation management APIs
    path('api/simulation/toggle/', views.SimulationToggleView.as_view(), name='simulation-toggle'),
    path('api/simulation/reset/', views.SimulationResetView.as_view(), name='simulation-reset'),
]

