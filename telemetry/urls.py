from django.urls import path
from . import views
from . import auth_views

app_name = 'telemetry'

urlpatterns = [
    # Auth Views
    path('login/', auth_views.UTMLoginView.as_view(), name='login'),
    path('logout/', auth_views.UTMLogoutView.as_view(), name='logout'),
    path('quick-login/<str:role>/', auth_views.UTMQuickLoginView.as_view(), name='quick-login'),
    
    path('register/', auth_views.UTMRegisterView.as_view(), name='register'),
    # Dashboard views
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('mobile/', views.MobilePageView.as_view(), name='mobile'),
    path('requests/', views.RequestsView.as_view(), name='requests'),
    path('status/', views.StatusView.as_view(), name='status'),
    path('history/', views.HistoryView.as_view(), name='history'),
    path('terms/', views.TermsView.as_view(), name='terms'),

    # Phone GPS Test Mode APIs
    path('api/phone-location/', views.PhoneLocationIngestView.as_view(), name='phone-location-ingest'),
    path('api/phone-location/latest/', views.PhoneLocationLatestView.as_view(), name='phone-location-latest'),
    path('api/phone-location/history/', views.PhoneLocationHistoryView.as_view(), name='phone-location-history'),

    # Core ESP32 & UTM Drone Telemetry APIs (Preserved for future hardware integration)
    path('api/telemetry/', views.TelemetryIngestView.as_view(), name='telemetry-ingest'),
    path('api/telemetry/latest/', views.TelemetryLatestView.as_view(), name='telemetry-latest'),
    path('api/telemetry/history/', views.TelemetryHistoryView.as_view(), name='telemetry-history'),
    path('api/telemetry/status/', views.DroneStatusView.as_view(), name='drone-status'),
    path('api/drones/all/', views.AllDronesLatestView.as_view(), name='all-drones-latest'),

    # Simulation management APIs
    path('api/simulation/toggle/', views.SimulationToggleView.as_view(), name='simulation-toggle'),
    path('api/simulation/reset/', views.SimulationResetView.as_view(), name='simulation-reset'),
    path('under-construction/', views.UnderConstructionView.as_view(), name='under_construction'),
    path('nosql-admin/', views.NoSQLAdminView.as_view(), name='nosql-admin'),
    path('dev-error/', views.DevErrorView.as_view(), name='dev-error'),
]



