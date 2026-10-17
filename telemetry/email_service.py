import secrets
import string
import logging
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User

logger = logging.getLogger('utm.email')


def generate_random_username(prefix='unit_'):
    """
    Generates a unique random username for an approved NCC Unit.
    Example: 'unit_48291'
    """
    for _ in range(100):
        random_digits = ''.join(secrets.choice(string.digits) for _ in range(5))
        username = f"{prefix}{random_digits}"
        if not User.objects.filter(username__iexact=username).exists():
            return username
    # Fallback with timestamp hex
    import time
    return f"{prefix}{int(time.time()) % 1000000}"


def generate_secure_password(length=9):
    """
    Generates a secure, readable random password with mixed-case letters and numbers.
    Avoids easily confused characters like 'O' and '0', 'l' and '1'.
    """
    chars = "abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ23456789!@#"
    while True:
        password = ''.join(secrets.choice(chars) for _ in range(length))
        # Ensure at least one uppercase, lowercase, digit, and symbol
        if (any(c.islower() for c in password) and
            any(c.isupper() for c in password) and
            any(c.isdigit() for c in password)):
            return password


def send_unit_credentials_email(profile, username, password, request=None):
    """
    Dispatches the official credentials email to the Unit's registered email address.
    Returns (success: bool, detail_message: str).
    """
    recipient_email = profile.user.email
    if not recipient_email:
        return False, "No email address found for this Unit profile."

    unit_name = profile.unit_name or profile.full_name or "NCC Unit"
    group_name = profile.group_name or "NCC Group HQ"
    dte_name = profile.dte_name or "NCC Directorate"

    if request:
        scheme = request.scheme
        host = request.get_host()
        login_url = f"{scheme}://{host}/login/"
    else:
        login_url = "http://127.0.0.1:8000/login/"

    subject = f"NCC DITN - Unit Approved & Official Login Credentials [{unit_name}]"

    plain_message = f"""JAI HIND!

Greetings from DGNCC Drone Operations Directorate.

Your Phase 1 Unit Registration has been APPROVED by DGNCC Admin.
Official login credentials have been assigned for your Unit to access the 
NCC Drone Identification & Tracking Network (NCC DITN).

----------------------------------------------------------------------
NCC UNIT DETAILS:
----------------------------------------------------------------------
Unit Name   : {unit_name}
Group HQ    : {group_name}
Directorate : {dte_name}
Official ID : #{profile.id}

----------------------------------------------------------------------
OFFICIAL LOGIN CREDENTIALS:
----------------------------------------------------------------------
Username : {username}
Password : {password}

Portal URL: {login_url}
----------------------------------------------------------------------

NEXT STEPS:
1. Navigate to {login_url}
2. Select 'Unit Login'
3. Enter your Username: '{username}' and the assigned Password.
4. Complete Phase 2: Enter Unit Station Base Location and register your NCC Drone Fleet / UIN.

IMPORTANT SECURITY NOTICE:
Keep these credentials confidential within authorized NCC Unit personnel.
Do not share login credentials with unauthorized individuals.

DGNCC Drone Operations Team
NCC Drone Identification & Tracking Network (NCC DITN)
Ministry of Defence, Government of India
"""

    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8fafc; margin: 0; padding: 20px; color: #1e293b; }}
            .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }}
            .header {{ background: #002D74; color: #ffffff; padding: 24px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 20px; letter-spacing: 1px; text-transform: uppercase; }}
            .header p {{ margin: 6px 0 0 0; font-size: 13px; opacity: 0.9; }}
            .content {{ padding: 28px; }}
            .badge-approved {{ display: inline-block; background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; padding: 4px 12px; border-radius: 9999px; font-weight: 700; font-size: 12px; margin-bottom: 16px; }}
            .card {{ background: #f1f5f9; border-left: 4px solid #002D74; padding: 16px; border-radius: 4px; margin: 20px 0; }}
            .card-title {{ font-size: 11px; text-transform: uppercase; font-weight: 800; color: #64748b; letter-spacing: 0.5px; margin-bottom: 8px; }}
            .cred-row {{ display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 14px; }}
            .cred-val {{ font-family: monospace; font-size: 16px; font-weight: 700; color: #002D74; background: #ffffff; padding: 4px 10px; border-radius: 4px; border: 1px solid #cbd5e1; }}
            .btn {{ display: inline-block; background: #002D74; color: #ffffff !important; padding: 12px 24px; border-radius: 4px; text-decoration: none; font-weight: 700; font-size: 14px; margin-top: 12px; text-align: center; }}
            .footer {{ background: #f8fafc; border-top: 1px solid #e2e8f0; padding: 16px; text-align: center; font-size: 11px; color: #64748b; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>NCC Drone Identification & Tracking Network</h1>
                <p>DGNCC Directorate &bull; Official Unit Onboarding</p>
            </div>
            <div class="content">
                <span class="badge-approved">&#10003; PHASE 1 REGISTRATION APPROVED BY DGNCC ADMIN</span>
                <p>Jai Hind!</p>
                <p>Your registration for <strong>{unit_name}</strong> (<em>{group_name} &bull; {dte_name}</em>) has been verified and accepted by DGNCC Admin.</p>
                
                <div class="card">
                    <div class="card-title">Official Unit Login Credentials</div>
                    <p style="margin: 4px 0 10px 0; font-size: 13px; color: #475569;">Use these credentials to sign in under <strong>Unit Login</strong>:</p>
                    <div style="margin-bottom: 10px;">
                        <span style="font-size: 12px; color: #64748b; display: block;">Username:</span>
                        <span class="cred-val">{username}</span>
                    </div>
                    <div>
                        <span style="font-size: 12px; color: #64748b; display: block;">Temporary Password:</span>
                        <span class="cred-val">{password}</span>
                    </div>
                </div>

                <p style="font-size: 13px; line-height: 1.5; color: #334155;">
                    <strong>Next Steps:</strong> Log in to complete <strong>Phase 2 Profile Verification</strong> (Unit Station coordinates, Remote Pilot details, and UAV fleet registration).
                </p>

                <div style="text-align: center; margin: 24px 0;">
                    <a href="{login_url}" class="btn">Login to NCC DITN Portal</a>
                </div>
            </div>
            <div class="footer">
                &copy; 2026 Directorate General NCC &bull; NCC DITN System. Ministry of Defence, Govt of India.<br>
                This is an automated operational notification. Please do not reply directly.
            </div>
        </div>
    </body>
    </html>
    """

    try:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'NCC DITN <noreply@ncc-ditn.gov.in>')
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False
        )
        logger.info(f"Credentials email sent successfully to {recipient_email} for user {username}")
        return True, f"Credentials email dispatched to {recipient_email} successfully."
    except Exception as err:
        logger.error(f"Failed to send email to {recipient_email}: {err}")
        return False, f"Email delivery error ({str(err)}). Credentials: Username={username}, Password={password}."
