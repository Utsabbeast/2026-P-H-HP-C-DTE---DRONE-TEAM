from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views import View
from django.contrib import messages
import os
import secrets
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

@method_decorator(never_cache, name='dispatch')
class UTMLoginView(View):
    """
    Renders the unified login portal and processes credentials.
    Supports:
      1. DGNCC Admin Login (DGNCC Admin Access: admin / admin123)
      2. NCC Unit Login (Unit Operator Access with assigned Username & Password)
      3. Guest Login (Read-Only Observer Access)
    """
    template_name = 'login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('telemetry:dashboard')
        
        mode = request.GET.get('mode', 'pilot') # 'atc' (DGNCC Admin) or 'pilot' (Unit) or 'guest'
        context = {
            'mode': mode,
            'atc_username': os.environ.get('ATC_ADMIN_USERNAME', 'admin'),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        login_type = request.POST.get('login_type', 'pilot') # 'atc', 'pilot', or 'guest'
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        # 1. Guest Login: Instant read-only access
        if login_type == 'guest':
            request.session['user_role'] = 'GUEST'
            request.session['user_role_label'] = 'Guest Observer (Read-Only)'
            request.session['user_name'] = 'Guest Viewer'
            messages.success(request, 'Logged in as Guest Observer with read-only access.')
            return redirect('/dashboard/?mode=main')

        if not username or not password:
            messages.error(request, 'Please provide both Username and Password.')
            return render(request, self.template_name, {'mode': login_type, 'username': username})

        # 2. Authenticate directly by username (and fallback to email/unit_name for resilience)
        user = authenticate(request, username=username, password=password)
        if user is None:
            # Fallback check by email
            matched_user = User.objects.filter(email__iexact=username).first()
            if not matched_user:
                # Fallback check by unit_name
                from telemetry.models import PilotProfile
                prof = PilotProfile.objects.filter(unit_name__iexact=username).first()
                if prof:
                    matched_user = prof.user
            if matched_user:
                user = authenticate(request, username=matched_user.username, password=password)

        if user is not None:
            login(request, user)
            
            # Login user without wiping hardware flight telemetry history
                
            # Determine role based on user attributes
            if user.is_superuser or user.is_staff:
                request.session['user_role'] = 'ATC'
                request.session['user_role_label'] = 'DGNCC Admin (All Access)'
                request.session['user_name'] = user.first_name or user.username
                messages.success(request, f'Logged in as DGNCC Admin. Welcome, {user.first_name or user.username}!')
                return redirect('/dashboard/?mode=main')
            elif login_type == 'atc':
                logout(request)
                request.session.flush()
                messages.error(request, 'Access Denied: Administrative credentials required for DGNCC Admin Login.')
                return render(request, self.template_name, {'mode': 'atc', 'username': username})
            else:
                from telemetry.models import PilotProfile
                profile, _ = PilotProfile.objects.get_or_create(user=user)

                # Check Phase 1 approval status
                if profile.phase1_status == 'PENDING':
                    logout(request)
                    request.session.flush()
                    messages.warning(
                        request,
                        'Your Unit registration is currently PENDING Phase 1 authorization by DGNCC Admin under Profile Acceptance. Once approved, your assigned credentials will be activated.'
                    )
                    return render(request, self.template_name, {'mode': 'pilot', 'username': username})

                if profile.phase1_status == 'REJECTED':
                    logout(request)
                    request.session.flush()
                    messages.error(
                        request,
                        'Your Unit registration request was REJECTED by DGNCC Admin. Please contact system administration.'
                    )
                    return render(request, self.template_name, {'mode': 'pilot', 'username': username})

                # Phase 1 is APPROVED!
                request.session['user_role'] = 'PILOT'
                request.session['user_role_label'] = 'Unit Operator'
                request.session['user_name'] = profile.unit_name or profile.full_name or user.first_name or user.username

                # Route based on Phase 2 profile completion status
                if profile.phase2_status == 'NOT_SUBMITTED':
                    messages.info(
                        request,
                        f'Phase 1 registration approved! Welcome, {profile.unit_name or user.username}. Please complete your Unit Profile and Drone assets for Phase 2 approval.'
                    )
                    return redirect('telemetry:profile')

                if profile.phase2_status == 'REJECTED':
                    messages.warning(
                        request,
                        'Your Phase 2 Unit Profile details were rejected by DGNCC Admin. Please review, edit, and re-submit your profile.'
                    )
                    return redirect('telemetry:profile')

                if profile.phase2_status == 'PENDING':
                    messages.info(
                        request,
                        f'Welcome, {profile.unit_name or user.username}! Your Unit Profile is under Phase 2 review by DGNCC Admin.'
                    )
                    return redirect('telemetry:dashboard')

                messages.success(request, f'Logged in as Unit Operator. Welcome, {profile.unit_name or user.username}!')
                return redirect('telemetry:dashboard')
        else:
            messages.error(request, 'Invalid credentials. Please check your Username and Password.')
            return render(request, self.template_name, {'mode': login_type, 'username': username})


class UTMQuickLoginView(View):
    """
    Provides 1-click quick login for testing & demonstration:
    - Quick DGNCC Admin Login
    - Quick Guest Observer Login
    """
    def get(self, request, role):
        if role == 'atc' or role == 'admin':
            username = os.environ.get('ATC_ADMIN_USERNAME', 'admin')
            password = os.environ.get('ATC_ADMIN_PASSWORD', 'admin123')
            user = authenticate(request, username=username, password=password)
            if not user:
                user = User.objects.filter(is_superuser=True).first()
            if user:
                login(request, user)
                # Preserve hardware flight telemetry on quick login
                request.session['user_role'] = 'ATC'
                request.session['user_role_label'] = 'DGNCC Admin (All Access)'
                messages.success(request, 'Logged in as DGNCC Admin (All Access).')
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('/dashboard/?mode=main')

        if role == 'guest':
            request.session['user_role'] = 'GUEST'
            request.session['user_role_label'] = 'Guest Observer (Read-Only)'
            request.session['user_name'] = 'Guest Viewer'
            messages.success(request, 'Logged in as Guest Observer with read-only access.')
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('/dashboard/?mode=main')

        messages.error(request, 'Quick login role unavailable. Please use Unit Login.')
        return redirect('telemetry:login')


class UTMLogoutView(View):
    """
    Logs out the current session and redirects to the login portal.
    """
    def get(self, request):
        logout(request)
        request.session.flush()
        
        # Preserve telemetry data across logout
            
        messages.success(request, 'You have been logged out safely.')
        next_url = request.GET.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('telemetry:login')
    
    def post(self, request):
        return self.get(request)


class UTMRegisterView(View):
    """
    Handles Phase 1 Unit Registration where the Unit creates their own
    Username and Password directly (no email system required).
    """
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('telemetry:dashboard')
        return render(request, 'register.html')

    def post(self, request):
        unit_name = request.POST.get('unit_name', '').strip()
        group_name = request.POST.get('group_name', '').strip()
        dte_name = request.POST.get('dte_name', '').strip()
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        context = {
            'unit_name': unit_name,
            'group_name': group_name,
            'dte_name': dte_name,
            'email': email,
            'username': username,
        }

        # Check required fields
        if not (unit_name and group_name and dte_name and email and username and password):
            messages.error(
                request,
                'Please fill in all required fields including Username and Password.'
            )
            return render(request, 'register.html', context)

        if password != confirm_password:
            messages.error(request, 'Passwords do not match. Please re-enter your password.')
            return render(request, 'register.html', context)

        if len(password) < 4:
            messages.error(request, 'Password must be at least 4 characters long.')
            return render(request, 'register.html', context)

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, f'Username "{username}" is already in use. Please select a different username.')
            return render(request, 'register.html', context)

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, f'Email address "{email}" is already registered. Please use another email or contact DGNCC Admin.')
            return render(request, 'register.html', context)

        from telemetry.models import PilotProfile
        if PilotProfile.objects.filter(unit_name__iexact=unit_name).exists():
            messages.error(request, f'Unit "{unit_name}" is already registered. Please contact DGNCC Admin.')
            return render(request, 'register.html', context)

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=unit_name
            )
            PilotProfile.objects.create(
                user=user,
                unit_name=unit_name,
                group_name=group_name,
                dte_name=dte_name,
                full_name=unit_name,
                ncc_unit=f"{group_name} / {dte_name}",
                initial_password=password,
                phase1_status='PENDING',
                phase2_status='NOT_SUBMITTED',
                status='PENDING'
            )
            messages.info(
                request,
                f'Registration submitted for NCC Unit "{unit_name}". '
                f'Your request has been submitted for authorization by DGNCC Admin in the Requests tab. '
                f'Once accepted, your account will be activated for login.'
            )
            return redirect('telemetry:login')
        except Exception as err:
            messages.error(request, f'Registration failed: {str(err)}')
            return render(request, 'register.html', context)
