import sys

content = open('telemetry/views.py', 'r', encoding='utf-8').read()

old_context = """        context['total_flying_drones'] = DroneTelemetry.objects.filter(received_at__gte=recent_time).values('drone_id').distinct().count()"""

new_context = """        context['total_flying_drones'] = DroneTelemetry.objects.filter(received_at__gte=recent_time).values('drone_id').distinct().count()
        
        # Check registration status for pilots
        if self.request.session.get('user_role') == 'PILOT' and self.request.user.is_authenticated:
            from .models import PilotProfile, DroneRegistration
            profile = PilotProfile.objects.filter(user=self.request.user, status='APPROVED').exists()
            drone = DroneRegistration.objects.filter(owner=self.request.user, status='APPROVED').exists()
            context['is_fully_registered'] = profile and drone
        else:
            context['is_fully_registered'] = True"""

if "context['is_fully_registered'] =" not in content:
    content = content.replace(old_context, new_context)

open('telemetry/views.py', 'w', encoding='utf-8').write(content)

print("Updated views.py with is_fully_registered")
