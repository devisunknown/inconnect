from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Send a test email through the configured email backend (e.g. Resend SMTP).'

    def add_arguments(self, parser):
        parser.add_argument('to', type=str, help='Destination email address.')

    def handle(self, *args, **options):
        to = options['to']
        subject = 'Test — InConnect email backend'
        message = (
            'This is a test email from InConnect.\n'
            f'Backend: {settings.EMAIL_BACKEND}\n'
            f'From: {settings.DEFAULT_FROM_EMAIL}\n'
            f'Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}\n'
            f'TLS: {settings.EMAIL_USE_TLS}\n'
            f'SITE_BASE_URL: {settings.SITE_BASE_URL}'
        )
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [to], fail_silently=False)
        except Exception as exc:  # noqa: BLE001 - surface any backend error
            raise CommandError(f'Email sending failed: {exc}') from exc
        self.stdout.write(
            self.style.SUCCESS(f'Test email sent to {to} via {settings.EMAIL_BACKEND}')
        )
