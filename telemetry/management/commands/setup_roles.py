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

        # 2. Unit 1 Profile: 1 Punjab Bn NCC -> PHHP&C Drone 1 (DRONE-3894D4BD2A58)
        u1, _ = User.objects.get_or_create(
            username='unit_punjab_1',
            defaults={
                'email': 'unit1.punjab@ncc-ditn.gov.in',
                'first_name': 'Rajesh',
                'last_name': 'Verma'
            }
        )
        u1.set_password('Unit123@Punjab')
        u1.email = 'unit1.punjab@ncc-ditn.gov.in'
        u1.first_name = 'Rajesh'
        u1.last_name = 'Verma'
        u1.is_staff = False
        u1.is_superuser = False
        u1.save()

        p1, _ = PilotProfile.objects.get_or_create(user=u1)
        p1.full_name = 'Lt. Col. Rajesh Verma'
        p1.unit_name = '1 Punjab Bn NCC'
        p1.group_name = 'Ludhiana Group HQ'
        p1.dte_name = 'PHHP&C Directorate'
        p1.phone_number = '+91 98765 43210'
        p1.ncc_wing = 'Army Wing'
        p1.ncc_unit = '1 Punjab Bn NCC, Ludhiana'
        p1.cadet_number = 'NCC/PB/26/1001'
        p1.base_location = 'Ludhiana Base Station'
        p1.license_number = 'DGCA-RPL-PB-2026-001'
        p1.organization = 'NCC DTE PHHP&C'
        p1.flying_experience_hours = 45.5
        p1.drone_model = 'PHHP&C Drone 1'
        p1.drone_uin = 'DRONE-3894D4BD2A58'
        p1.phase1_status = 'APPROVED'
        p1.phase2_status = 'APPROVED'
        p1.status = 'APPROVED'
        p1.phase1_reviewed_at = timezone.now()
        p1.phase2_reviewed_at = timezone.now()
        p1.initial_password = 'Unit123@Punjab'
        p1.admin_notes = 'Verified Unit Profile & Drone Assignment'
        p1.save()

        d1, _ = DroneRegistration.objects.get_or_create(uin='DRONE-3894D4BD2A58', defaults={'owner': u1, 'name': 'PHHP&C Drone 1'})
        d1.owner = u1
        d1.name = 'PHHP&C Drone 1'
        d1.category = 'MICRO'
        d1.max_altitude_m = 120.0
        d1.status = 'APPROVED'
        d1.save()
        self.stdout.write(self.style.SUCCESS('Unit 1 Profile & Drone 1 (DRONE-3894D4BD2A58) verified.'))

        # 3. Unit 2 Profile: 2 Punjab Air Sqn NCC -> PHHP&C Drone 2 (DRONE-40573255F188)
        u2, _ = User.objects.get_or_create(
            username='unit_punjab_2',
            defaults={
                'email': 'unit2.punjab@ncc-ditn.gov.in',
                'first_name': 'Amit',
                'last_name': 'Sharma'
            }
        )
        u2.set_password('Unit123@Punjab')
        u2.email = 'unit2.punjab@ncc-ditn.gov.in'
        u2.first_name = 'Amit'
        u2.last_name = 'Sharma'
        u2.is_staff = False
        u2.is_superuser = False
        u2.save()

        p2, _ = PilotProfile.objects.get_or_create(user=u2)
        p2.full_name = 'Wing Cdr. Amit Sharma'
        p2.unit_name = '2 Punjab Air Sqn NCC'
        p2.group_name = 'Amritsar Group HQ'
        p2.dte_name = 'PHHP&C Directorate'
        p2.phone_number = '+91 98765 43211'
        p2.ncc_wing = 'Air Wing'
        p2.ncc_unit = '2 Punjab Air Sqn NCC, Amritsar'
        p2.cadet_number = 'NCC/PB/26/1002'
        p2.base_location = 'Amritsar Air Base'
        p2.license_number = 'DGCA-RPL-PB-2026-002'
        p2.organization = 'NCC DTE PHHP&C'
        p2.flying_experience_hours = 62.0
        p2.drone_model = 'PHHP&C Drone 2'
        p2.drone_uin = 'DRONE-40573255F188'
        p2.phase1_status = 'APPROVED'
        p2.phase2_status = 'APPROVED'
        p2.status = 'APPROVED'
        p2.phase1_reviewed_at = timezone.now()
        p2.phase2_reviewed_at = timezone.now()
        p2.initial_password = 'Unit123@Punjab'
        p2.admin_notes = 'Verified Unit Profile & Drone Assignment'
        p2.save()

        d2, _ = DroneRegistration.objects.get_or_create(uin='DRONE-40573255F188', defaults={'owner': u2, 'name': 'PHHP&C Drone 2'})
        d2.owner = u2
        d2.name = 'PHHP&C Drone 2'
        d2.category = 'MICRO'
        d2.max_altitude_m = 120.0
        d2.status = 'APPROVED'
        d2.save()
        self.stdout.write(self.style.SUCCESS('Unit 2 Profile & Drone 2 (DRONE-40573255F188) verified.'))
