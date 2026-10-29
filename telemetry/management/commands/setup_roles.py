import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

class Command(BaseCommand):
    help = 'Ensures admin and verified unit pilot accounts/drones exist on Render and local environments.'

    def handle(self, *args, **options):
        from telemetry.models import PilotProfile, DroneRegistration

        # Remove legacy test users if present
        User.objects.filter(username__in=['admin_atc', 'pilot_user', 'guest']).delete()

        # 1. Sole Superuser / ATC Admin
        admin_username = 'admin'
        admin_password = 'admin123'
        admin_user, created = User.objects.get_or_create(
            username=admin_username,
            defaults={
                'email': 'admin@ncc-ditn.gov.in',
                'first_name': 'ATC Admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password(admin_password)
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        self.stdout.write(self.style.SUCCESS(f'Admin user verified: {admin_username}'))

        # 2. Unit 1 Profile: Jalandhar Group -> PHHP&C Drone 1 (DRONE-3894D4BD2A58)
        u1 = User.objects.filter(username='unit_punjab_1').first()
        if u1:
            u1.username = 'Jalandhar Group'
            u1.save()
        else:
            u1, _ = User.objects.get_or_create(
                username='Jalandhar Group',
                defaults={
                    'email': 'jalandhar.group@ncc-ditn.gov.in',
                    'first_name': 'Jalandhar',
                    'last_name': 'Group'
                }
            )
        u1.set_password('Jalandhar123@group')
        u1.email = 'jalandhar.group@ncc-ditn.gov.in'
        u1.first_name = 'Jalandhar'
        u1.last_name = 'Group'
        u1.is_staff = False
        u1.is_superuser = False
        u1.save()

        p1, _ = PilotProfile.objects.get_or_create(user=u1)
        p1.full_name = 'Col. Jalandhar Group HQ'
        p1.unit_name = 'Jalandhar Group'
        p1.group_name = 'Jalandhar Group HQ'
        p1.dte_name = 'PHHP&C Directorate'
        p1.phone_number = '+91 98765 43210'
        p1.ncc_wing = 'Army Wing'
        p1.ncc_unit = 'Jalandhar Group NCC, Jalandhar'
        p1.cadet_number = 'NCC/PB/JL/26/1001'
        p1.base_location = 'Jalandhar Base Station'
        p1.license_number = 'DGCA-RPL-PB-2026-001'
        p1.organization = 'NCC DTE PHHP&C'
        p1.flying_experience_hours = 48.0
        p1.drone_model = 'PHHP&C Drone 1'
        p1.drone_uin = 'DRONE-3894D4BD2A58'
        p1.phase1_status = 'APPROVED'
        p1.phase2_status = 'APPROVED'
        p1.status = 'APPROVED'
        p1.phase1_reviewed_at = timezone.now()
        p1.phase2_reviewed_at = timezone.now()
        p1.initial_password = 'Jalandhar123@group'
        p1.admin_notes = 'Verified Jalandhar Group Unit Profile & Drone Assignment'
        p1.save()

        d1, _ = DroneRegistration.objects.get_or_create(uin='DRONE-3894D4BD2A58', defaults={'owner': u1, 'name': 'PHHP&C Drone 1'})
        d1.owner = u1
        d1.name = 'PHHP&C Drone 1'
        d1.category = 'MICRO'
        d1.max_altitude_m = 120.0
        d1.status = 'APPROVED'
        d1.save()
        self.stdout.write(self.style.SUCCESS('Jalandhar Group Profile & Drone 1 (DRONE-3894D4BD2A58) verified.'))

        # 3. Unit 2 Profile: Ambala Group -> PHHP&C Drone 2 (DRONE-40573255F188)
        u2 = User.objects.filter(username='unit_punjab_2').first()
        if u2:
            u2.username = 'Ambala Group'
            u2.save()
        else:
            u2, _ = User.objects.get_or_create(
                username='Ambala Group',
                defaults={
                    'email': 'ambala.group@ncc-ditn.gov.in',
                    'first_name': 'Ambala',
                    'last_name': 'Group'
                }
            )
        u2.set_password('Ambala123@group')
        u2.email = 'ambala.group@ncc-ditn.gov.in'
        u2.first_name = 'Ambala'
        u2.last_name = 'Group'
        u2.is_staff = False
        u2.is_superuser = False
        u2.save()

        p2, _ = PilotProfile.objects.get_or_create(user=u2)
        p2.full_name = 'Wing Cdr. Ambala Group HQ'
        p2.unit_name = 'Ambala Group'
        p2.group_name = 'Ambala Group HQ'
        p2.dte_name = 'PHHP&C Directorate'
        p2.phone_number = '+91 98765 43211'
        p2.ncc_wing = 'Air Wing'
        p2.ncc_unit = 'Ambala Group NCC, Ambala'
        p2.cadet_number = 'NCC/HR/AM/26/1002'
        p2.base_location = 'Ambala Air Base'
        p2.license_number = 'DGCA-RPL-HR-2026-002'
        p2.organization = 'NCC DTE PHHP&C'
        p2.flying_experience_hours = 65.0
        p2.drone_model = 'PHHP&C Drone 2'
        p2.drone_uin = 'DRONE-40573255F188'
        p2.phase1_status = 'APPROVED'
        p2.phase2_status = 'APPROVED'
        p2.status = 'APPROVED'
        p2.phase1_reviewed_at = timezone.now()
        p2.phase2_reviewed_at = timezone.now()
        p2.initial_password = 'Ambala123@group'
        p2.admin_notes = 'Verified Ambala Group Unit Profile & Drone Assignment'
        p2.save()

        d2, _ = DroneRegistration.objects.get_or_create(uin='DRONE-40573255F188', defaults={'owner': u2, 'name': 'PHHP&C Drone 2'})
        d2.owner = u2
        d2.name = 'PHHP&C Drone 2'
        d2.category = 'MICRO'
        d2.max_altitude_m = 120.0
        d2.status = 'APPROVED'
        d2.save()
        self.stdout.write(self.style.SUCCESS('Ambala Group Profile & Drone 2 (DRONE-40573255F188) verified.'))
