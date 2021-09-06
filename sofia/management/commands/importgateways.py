""" Management utility to manage Gateways. """
import ast
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from sofia.models import Gateway, AclAddress


class Command(BaseCommand):
    """ A command to manage sofia profiles. """

    help = 'Used to manage sofia profiles.'
    requires_migrations_checks = True

    @staticmethod
    def update_gateway(gateway, data):
        """ Update and save gateway values. """
        changed = False
        for key, value in data.items():
            try:
                if getattr(gateway, key) != value:
                    setattr(gateway, key, value)
                    changed = True
            except AttributeError:
                continue
        if changed:
            gateway.save()
            print('Changed gateway', gateway, '- reload mod_sofia')

    @staticmethod
    def manage_gateways(gateways):
        """ CRUD gateway and ACL address objects. """

        # Delete gateway profiles
        for gateway in Gateway.objects.all():
            if gateway.domain not in gateways:
                objects = gateway.delete()
                print('Deleted gateway', objects, '- reload mod_sofia')
                objects = AclAddress.objects.filter(gateway=gateway).delete()
                print('Deleted ACL address', objects,
                      '- restart netfilter-persistent pbx-web')

        # Update gateway profiles.
        for domain, data in gateways.items():
            try:
                gateway = Gateway.objects.get(domain=domain)
                Command.update_gateway(gateway, data)
            except Gateway.DoesNotExist:
                gateway = Gateway.objects.create(
                    domain=domain,
                    port=data['port'],
                    username=data['username'],
                    password=data['password'],
                    proxy=data['proxy'],
                    realm=data['realm'],
                    priority=data['priority']
                )
                print('Created gateway', gateway, '- reload mod_sofia')

            # Add ACL addresses.
            for address in data['allow_list']:
                acl, created = AclAddress.objects.get_or_create(
                    address=address, gateway=gateway
                )
                if created:
                    print('Created ACL address', acl,
                          '- restart netfilter-persistent pbx-web')

            # Delete ACL addresses.
            for addr in AclAddress.objects.filter(gateway=gateway):
                if addr.address not in data['allow_list']:
                    objects = addr.delete()
                    print('Deleted ACL address', objects,
                          '- restart netfilter-persistent pbx-web')

    def handle(self, *args, **options):
        """ Manage sofia profiles. """
        sofia_file = os.path.join(settings.BASE_DIR, 'var', 'sofia.py')
        with open(sofia_file) as sofia_fd:
            config = ast.literal_eval(sofia_fd.read())
        if config.get('GATEWAYS'):
            self.manage_gateways(config['GATEWAYS'])
