from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views import View
from django.contrib import messages
import os
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

@method_decorator(never_cache, name='dispatch')
class UTMLoginView(View):
    """
    Renders the unified 3-way login portal and processes user credentials.
    Supports:
      1. ATC Controller Login (All Access Admin)
      2. Registered Pilot Login (User Access)
      3. Guest Access (Read-Only Observer)
    """
    template_name = 'login.html'

    def get(self, request):
        # Allow guests to view the login page so they can register or login properly
        if request.user.is_authenticated and request.user.username != 'guest':
            return redirect('telemetry:dashboard')
        
        mode = request.GET.get('mode', 'atc') # 'atc', 'pilot', or 'guest'
        context = {
            'mode': mode,
            'atc_username': os.environ.get('ATC_ADMIN_USERNAME', 'admin_atc'),
            'pilot_username': os.environ.get('PILOT_USER_USERNAME', 'pilot_user'),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        login_type = request.POST.get('login_type', 'atc') # 'atc', 'pilot', or 'guest'
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        # Handle Guest Access directly
        if login_type == 'guest':
            return self._login_as_guest(request)

        if not username or not password:
            messages.error(request, 'Please provide both username and password.')
            return render(request, self.template_name, {'mode': login_type, 'username': username})

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            # Reset map data / telemetry history on login as requested
            try:
                from telemetry.models import PhoneTelemetry, DroneTelemetry
                PhoneTelemetry.objects.all().delete()
                DroneTelemetry.objects.all().delete()
            except Exception:
                pass
                
            # Determine role based on user attributes or login choice
            if user.is_superuser or user.is_staff or login_type == 'atc':
                request.session['user_role'] = 'ATC'
                request.session['user_role_label'] = 'ATC Controller (All Access)'
            else:
                request.session['user_role'] = 'PILOT'
                request.session['user_role_label'] = 'Pilot Operator'
            
            role_label = "ATC Admin" if request.session['user_role'] == 'ATC' else "Pilot Operator"
            messages.success(request, f'Logged in as {role_label}. Welcome, {user.first_name or user.username}!')
            if request.session['user_role'] == 'ATC':
                return redirect('/dashboard/?mode=main')
            return redirect('telemetry:dashboard')
        else:
            messages.error(request, 'Invalid credentials. Please check your username and password.')
            return render(request, self.template_name, {'mode': login_type, 'username': username})

    def _login_as_guest(self, request):
        # Authenticate with standard guest user or set session
        guest_user = User.objects.filter(username='guest').first()
        if guest_user:
            login(request, guest_user)
            
        # Reset map data / telemetry history on guest login as requested
        try:
            from telemetry.models import PhoneTelemetry, DroneTelemetry
            PhoneTelemetry.objects.all().delete()
            DroneTelemetry.objects.all().delete()
        except Exception:
            pass
            
        request.session['user_role'] = 'GUEST'
        request.session['user_role_label'] = 'Guest Observer (Read-Only)'
        messages.success(request, 'Logged in as Guest Observer with read-only access.')
        return redirect('telemetry:dashboard')


class UTMQuickLoginView(View):
    """
    Provides 1-click quick logins for testing & demonstration:
    - Quick ATC Login
    - Quick Pilot Login
    - Quick Guest Login
    """
    def get(self, request, role):
        if role == 'atc':
            username = os.environ.get('ATC_ADMIN_USERNAME', 'admin_atc')
            password = os.environ.get('ATC_ADMIN_PASSWORD', 'atcpass123')
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                try:
                    from telemetry.models import PhoneTelemetry, DroneTelemetry
                    PhoneTelemetry.objects.all().delete()
                    DroneTelemetry.objects.all().delete()
                except Exception:
                    pass
                request.session['user_role'] = 'ATC'
                request.session['user_role_label'] = 'ATC Controller (All Access)'
                messages.success(request, 'Logged in as ATC Controller (All Access).')
                return redirect('/dashboard/?mode=main')

        elif role == 'pilot':
            username = os.environ.get('PILOT_USER_USERNAME', 'pilot_user')
            password = os.environ.get('PILOT_USER_PASSWORD', 'pilotpass123')
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                try:
                    from telemetry.models import PhoneTelemetry, DroneTelemetry
                    PhoneTelemetry.objects.all().delete()
                    DroneTelemetry.objects.all().delete()
                except Exception:
                    pass
                request.session['user_role'] = 'PILOT'
                request.session['user_role_label'] = 'Pilot Operator'
                messages.success(request, 'Logged in as Registered Pilot.')
                return redirect('telemetry:dashboard')

        elif role == 'guest':
            guest_user = User.objects.filter(username='guest').first()
            if guest_user:
                login(request, guest_user)
            request.session['user_role'] = 'GUEST'
            request.session['user_role_label'] = 'Guest Observer (Read-Only)'
            messages.success(request, 'Logged in as Guest Observer.')
            return redirect('telemetry:dashboard')

        messages.error(request, 'Invalid quick login role requested.')
        return redirect('telemetry:login')


class UTMLogoutView(View):
    """
    Logs out the current session and redirects to the 3-way login portal.
    """
    def get(self, request):
        is_guest = request.session.get('user_role') == 'GUEST'
        logout(request)
        request.session.flush()
        
        # Reset map data / telemetry history on logout as requested
        try:
            from telemetry.models import PhoneTelemetry, DroneTelemetry
            PhoneTelemetry.objects.all().delete()
            DroneTelemetry.objects.all().delete()
        except Exception:
            pass
            
        if is_guest:
            messages.success(request, 'You have been logged out safely.')
        else:
            messages.success(request, 'You have been logged out safely.')
            
        next_url = request.GET.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('telemetry:login')
    
    def post(self, request):
        return self.get(request)



class UTMRegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        context = {
            'custom_message': 'We are not taking any registrations right now because the website is under development.',
            'custom_title': 'Registration Unavailable'
        }
        return render(request, '404.html', context, status=403)

