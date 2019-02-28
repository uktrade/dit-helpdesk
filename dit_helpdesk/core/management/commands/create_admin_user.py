import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):

        if User.objects.filter(username='dit_helpdesk_admin').exists():
            return

        if not os.environ.get('DIT_HELPDESK_ADMIN_PASSWORD'):
            raise Exception('env variable DIT_HELPDESK_ADMIN_PASSWORD is not set')

        User.objects.create_superuser(
            'dit_helpdesk_admin',
            'dit_helpdesk@digital.trade.gov.uk.com',  # NOTE: this email address doesn't exist
            os.environ['DIT_HELPDESK_ADMIN_PASSWORD']
        )
