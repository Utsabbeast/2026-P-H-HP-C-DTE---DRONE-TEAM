import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    help = 'Ensures default ATC Admin, Pilot User, and Guest accounts exist.'

    def handle(self, *args, **options):
        # 1. ATC Admin Account (All Access)
        atc_username = os.environ.get('ATC_ADMIN_USERNAME', 'admin_atc')
        atc_password = os.environ.get('ATC_ADMIN_PASSWORD', 'atcpass123')
        
        atc_user, created = User.objects.get_or_create(
            username=atc_username,
            defaults={
                'email': 'atc@utm-drone.local',
                'first_name': 'ATC Airspace',
                'last_name': 'Controller',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        atc_user.set_password(atc_password)
        atc_user.is_staff = True
        atc_user.is_superuser = True
        atc_user.save()
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created ATC Admin user: {atc_username}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Updated ATC Admin user password: {atc_username}'))

        # 2. Pilot User Account (Operator Access)
        pilot_username = os.environ.get('PILOT_USER_USERNAME', 'pilot_user')
        pilot_password = os.environ.get('PILOT_USER_PASSWORD', 'pilotpass123')
        
        pilot_user, created = User.objects.get_or_create(
            username=pilot_username,
            defaults={
                'email': 'pilot@utm-drone.local',
                'first_name': 'Registered',
                'last_name': 'Pilot',
                'is_staff': False,
                'is_superuser': False,
            }
        )
        pilot_user.set_password(pilot_password)
        pilot_user.save()
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created Pilot user: {pilot_username}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Updated Pilot user password: {pilot_username}'))

        # 3. Guest Account (Read-Only Access)
        guest_username = 'guest'
        guest_user, created = User.objects.get_or_create(
            username=guest_username,
            defaults={
                'email': 'guest@utm-drone.local',
                'first_name': 'Guest',
                'last_name': 'Observer',
                'is_staff': False,
                'is_superuser': False,
            }
        )
        guest_user.set_password('guestpass123')
        guest_user.save()
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created Guest user account'))

        self.stdout.write(self.style.SUCCESS('Role setup completed successfully!'))
