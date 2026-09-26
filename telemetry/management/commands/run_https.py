import os
import ssl
import subprocess
from wsgiref.simple_server import make_server
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.wsgi import get_wsgi_application
from django.contrib.staticfiles.handlers import StaticFilesHandler

from telemetry.views import get_local_ip


class Command(BaseCommand):
    help = 'Runs a lightweight local development HTTPS server to allow Android Chrome Geolocation over local Wi-Fi.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--bind',
            default='0.0.0.0',
            help='IP address to bind the server to (default: 0.0.0.0)'
        )
        parser.add_argument(
            '--port',
            type=int,
            default=8443,
            help='Port number to run HTTPS on (default: 8443)'
        )
        parser.add_argument(
            '--cert',
            default=None,
            help='Path to SSL certificate file (default: auto-generated in ssl/cert.pem)'
        )
        parser.add_argument(
            '--key',
            default=None,
            help='Path to SSL private key file (default: auto-generated in ssl/key.pem)'
        )

    def handle(self, *args, **options):
        bind_host = options['bind']
        port = options['port']
        cert_path = options['cert']
        key_path = options['key']

        ssl_dir = os.path.join(settings.BASE_DIR, 'ssl')
        os.makedirs(ssl_dir, exist_ok=True)

        if not cert_path:
            cert_path = os.path.join(ssl_dir, 'cert.pem')
        if not key_path:
            key_path = os.path.join(ssl_dir, 'key.pem')

        # Auto-generate self-signed cert if missing
        if not os.path.exists(cert_path) or not os.path.exists(key_path):
            self.stdout.write(self.style.WARNING("Generating temporary development SSL certificate in ssl/ ..."))
            cmd = [
                'openssl', 'req', '-x509', '-newkey', 'rsa:2048',
                '-keyout', key_path,
                '-out', cert_path,
                '-days', '365',
                '-nodes',
                '-subj', '/CN=utm-local-dev'
            ]
            try:
                subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.stdout.write(self.style.SUCCESS(f"SSL certificate generated: {cert_path}"))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Failed to generate self-signed cert: {e}"))
                return

        local_ip = get_local_ip()

        self.stdout.write(self.style.SUCCESS("\n" + "=" * 70))
        self.stdout.write(self.style.SUCCESS("  UTM SECURE HTTPS DEVELOPMENT SERVER RUNNING"))
        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write(f"Listening on: https://{bind_host}:{port}/\n")
        self.stdout.write(self.style.NOTICE("1. On this laptop, open the UTM Dashboard:"))
        self.stdout.write(self.style.SUCCESS(f"   https://localhost:{port}/dashboard/"))
        self.stdout.write(self.style.NOTICE(f"   (or https://{local_ip}:{port}/dashboard/)\n"))
        self.stdout.write(self.style.NOTICE("2. On the Android phone connected to hotspot, open:"))
        self.stdout.write(self.style.SUCCESS(f"   https://{local_ip}:{port}/mobile/\n"))
        self.stdout.write(self.style.WARNING("⚠️ Note for Android Chrome:"))
        self.stdout.write("   Because this uses a self-signed certificate, Android Chrome will show:")
        self.stdout.write("   'Your connection is not private'.")
        self.stdout.write("   Tap 'Advanced' -> 'Proceed to <IP> (unsafe)' to proceed.")
        self.stdout.write("   Chrome will then grant full Geolocation permissions!\n")
        self.stdout.write("Press CTRL+C to stop the server.\n" + "=" * 70 + "\n")

        # Wrap Django WSGI application with static files handler
        wsgi_app = StaticFilesHandler(get_wsgi_application())

        httpd = make_server(bind_host, port, wsgi_app)

        # Configure SSL context
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=cert_path, keyfile=key_path)
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS("\nHTTPS Server stopped cleanly."))
