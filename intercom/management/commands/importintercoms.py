""" Management utility to manage Intercom profiles. """
import ast
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from intercom.models import Intercom


class Command(BaseCommand):
    """ A command to manage Intercom profiles. """

    help = 'Used to manage Intercom profiles.'
    requires_migrations_checks = True

    @staticmethod
    def manage_intercoms(intercoms):
        """ CRUD Intercoms. """

        # Delete intercom profiles.
        for intercom in Intercom.objects.all():
            if intercom.domain not in intercoms:
                objects = intercom.delete()
                print('Deleted intercom', objects, '- reload mod_sofia')

        # Add intercom profiles.
        for domain, port in intercoms.items():
            intercom, created = Intercom.objects.get_or_create(
                domain=domain, port=port
            )
            if created:
                print('Created intercom', intercom, '- reload mod_sofia')
            elif intercom.port != port:
                intercom.update(port=port)
                intercom.save()
                print('Changed intercom', intercom, '- reload mod_sofia')

    def handle(self, *args, **options):
        """ Manage Intercom profiles. """
        intercom_file = os.path.join(settings.BASE_DIR, 'var', 'intercom.py')
        with open(intercom_file) as intercom_fd:
            config = ast.literal_eval(intercom_fd.read())
        if config.get('INTERCOMS'):
            self.manage_intercoms(config['INTERCOMS'])
        else:
            print('No Intercoms found')
