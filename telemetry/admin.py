from django.contrib import admin
from .models import DroneTelemetry, PhoneTelemetry


@admin.register(DroneTelemetry)
class DroneTelemetryAdmin(admin.ModelAdmin):
    list_display = (
        'drone_id',
        'latitude',
        'longitude',
        'altitude',
        'heading',
        'timestamp',
        'received_at',
        'is_connected_badge',
    )
    list_filter = ('drone_id', 'received_at')
    search_fields = ('drone_id',)
    readonly_fields = ('received_at',)
    ordering = ('-received_at',)
    list_per_page = 50

    @admin.display(description='Status')
    def is_connected_badge(self, obj):
        return "🟢 Active" if obj.is_connected() else "⚪ Stale"


@admin.register(PhoneTelemetry)
class PhoneTelemetryAdmin(admin.ModelAdmin):
    list_display = (
        'device_id',
        'latitude',
        'longitude',
        'altitude',
        'heading',
        'accuracy',
        'speed',
        'source',
        'timestamp',
        'received_at',
        'is_connected_badge',
    )
    list_filter = ('device_id', 'source', 'received_at')
    search_fields = ('device_id',)
    readonly_fields = ('received_at',)
    ordering = ('-received_at',)
    list_per_page = 50

    @admin.display(description='Status')
    def is_connected_badge(self, obj):
        return "🟢 Active" if obj.is_connected() else "⚪ Stale"

