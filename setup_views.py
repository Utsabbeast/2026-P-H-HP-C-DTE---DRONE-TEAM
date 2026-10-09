import sys
import os

content = open('telemetry/models.py', 'r', encoding='utf-8').read()

if 'pilot = models.ForeignKey(User' not in content:
    content = content.replace("class FlightPermissionRequest(models.Model):", "class FlightPermissionRequest(models.Model):\n    pilot = models.ForeignKey(User, on_delete=models.CASCADE, related_name='flight_requests', null=True)")

open('telemetry/models.py', 'w', encoding='utf-8').write(content)

# Update views.py for RequestsView and StatusView
views_content = open('telemetry/views.py', 'r', encoding='utf-8').read()

old_requests_view = """class RequestsView(TemplateView):
    template_name = 'requests.html'"""

new_requests_view = """class RequestsView(TemplateView):
    template_name = 'requests.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import FlightPermissionRequest, DroneRegistration, PilotProfile
        context['is_atc'] = self.request.session.get('user_role') == 'ATC' or self.request.user.is_superuser
        context['flight_requests'] = FlightPermissionRequest.objects.all()
        context['drone_registrations'] = DroneRegistration.objects.all()
        context['profile_requests'] = PilotProfile.objects.all()
        return context
"""
if "context['flight_requests'] = FlightPermissionRequest" not in views_content:
    views_content = views_content.replace(old_requests_view, new_requests_view)


old_status_view = """    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_role'] = self.request.session.get('user_role', 'GUEST')
        context['user_role_label'] = self.request.session.get('user_role_label', 'Guest Observer (Read-Only)')
        context['latest_request'] = FlightPermissionRequest.objects.first()
        return context"""

new_status_view = """    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import FlightPermissionRequest, DroneRegistration, PilotProfile
        context['user_role'] = self.request.session.get('user_role', 'GUEST')
        context['user_role_label'] = self.request.session.get('user_role_label', 'Guest Observer (Read-Only)')
        
        if self.request.user.is_authenticated:
            context['pilot_profile'] = PilotProfile.objects.filter(user=self.request.user).first()
            context['drone_registration'] = DroneRegistration.objects.filter(owner=self.request.user).first()
            context['flight_requests'] = FlightPermissionRequest.objects.filter(pilot=self.request.user).order_by('-created_at')
        return context"""

if "context['pilot_profile'] = PilotProfile" not in views_content:
    views_content = views_content.replace(old_status_view, new_status_view)

# Update POST in StatusView to handle multiple forms
old_post = """    def post(self, request, *args, **kwargs):
        FlightPermissionRequest.objects.create(
            location_name=request.POST.get('locName', 'Unknown'),
            latitude=request.POST.get('locLat', 0.0) or 0.0,
            longitude=request.POST.get('locLon', 0.0) or 0.0,
            max_altitude=request.POST.get('maxAlt', 0.0) or 0.0,
            purpose=request.POST.get('purpose', ''),
            status='PENDING'
        )
        messages.error(request, 'We are not accepting any request right now because website is under development.')
        return redirect('telemetry:status')"""

new_post = """    def post(self, request, *args, **kwargs):
        from .models import FlightPermissionRequest, DroneRegistration, PilotProfile
        form_type = request.POST.get('form_type')
        
        if form_type == 'profile':
            PilotProfile.objects.create(
                user=request.user,
                license_number=request.POST.get('license', ''),
                status='PENDING'
            )
            messages.success(request, 'Profile submitted for ATC approval.')
            
        elif form_type == 'drone':
            DroneRegistration.objects.create(
                owner=request.user,
                name=request.POST.get('drone_name', ''),
                uin=request.POST.get('uin', ''),
                category=request.POST.get('category', 'MICRO'),
                max_altitude_m=float(request.POST.get('max_alt', 120.0)),
                status='PENDING'
            )
            messages.success(request, 'Drone registration submitted for ATC approval.')
            
        elif form_type == 'flight':
            FlightPermissionRequest.objects.create(
                pilot=request.user if request.user.is_authenticated else None,
                location_name=request.POST.get('locName', 'Unknown'),
                latitude=request.POST.get('locLat', 0.0) or 0.0,
                longitude=request.POST.get('locLon', 0.0) or 0.0,
                max_altitude=request.POST.get('maxAlt', 0.0) or 0.0,
                purpose=request.POST.get('purpose', ''),
                status='PENDING'
            )
            messages.error(request, 'We are not accepting any request right now because website is under development.')
            
        return redirect('telemetry:status')"""

if "form_type == 'profile'" not in views_content:
    views_content = views_content.replace(old_post, new_post)

open('telemetry/views.py', 'w', encoding='utf-8').write(views_content)

print("Updated views and models")
