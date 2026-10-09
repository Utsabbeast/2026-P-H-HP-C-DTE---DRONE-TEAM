import sys

# 1. Update urls.py
content = open('telemetry/urls.py', 'r', encoding='utf-8').read()
content = content.replace("path('api/telemetry/status/', views.DroneStatusView.as_view(), name='drone-status'),",
    "path('api/telemetry/status/', views.DroneStatusView.as_view(), name='drone-status'),\n    path('api/drones/all/', views.AllDronesLatestView.as_view(), name='all-drones-latest'),")
open('telemetry/urls.py', 'w', encoding='utf-8').write(content)

# 2. Update views.py
view_code = """
class AllDronesLatestView(APIView):
    authentication_classes = []
    permission_classes = []
    
    def get(self, request, *args, **kwargs):
        from .models import DroneTelemetry
        from .serializers import DroneTelemetrySerializer
        
        # Get distinct drone IDs that are not simulated
        drone_ids = DroneTelemetry.objects.filter(is_simulated=False).values_list('drone_id', flat=True).distinct()
        
        latest_records = []
        for d_id in drone_ids:
            latest = DroneTelemetry.objects.filter(drone_id=d_id, is_simulated=False).order_by('-received_at').first()
            if latest:
                latest_records.append(latest)
                
        serializer = DroneTelemetrySerializer(latest_records, many=True)
        return Response({
            "status": "success",
            "count": len(latest_records),
            "results": serializer.data
        })
"""
content = open('telemetry/views.py', 'r', encoding='utf-8').read()
if "AllDronesLatestView" not in content:
    content = content + '\n' + view_code
open('telemetry/views.py', 'w', encoding='utf-8').write(content)

print('Updated URLs and Views')
