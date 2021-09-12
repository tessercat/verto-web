""" Management utility to manage SignalWire gateway addresses. """
import ast
import os
from pprint import pformat
import dns.resolver
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    """ A command to manage SignalWire gateway addresses. """

    help = 'Used to manage SignalWire gateway addresses.'
    requires_migrations_checks = True

    @staticmethod
    def update_profile_addrs(profile):
        """ Update and profile addresses and return True if changed. """
        changed = False
        current = {}
        answer = dns.resolver.resolve('sip.signalwire.com', 'A')
        for rdata in answer:
            current[rdata.to_text()] = {'rdata': rdata, 'status': 'new'}
        for addr in profile['allow_list']:
            if addr in current:
                current[addr]['status'] = 'exists'
            else:
                current[addr] = {
                    'addr': addr,
                    'status': 'removed'
                }
        for addr, data in current.items():
            print(data)
            if data['status'] == 'new':
                profile['allow_list'].append(addr)
                changed = True
            elif data['status'] == 'removed':
                profile['allow_list'].remove(addr)
                changed = True
        return changed

    def handle(self, *args, **options):
        """ Manage sofia profiles. """
        sofia_file = os.path.join(settings.BASE_DIR, 'var', 'sofia.py')
        with open(sofia_file) as sofia_fd:
            config = ast.literal_eval(sofia_fd.read())
        old_profile = config['GATEWAYS'].get('signalwire')
        if old_profile:
            if self.update_profile_addrs(old_profile):
                backup_file = os.path.join(
                    settings.BASE_DIR, 'var', '~sofia.py'
                )
                os.rename(sofia_file, backup_file)
                with open(sofia_file, 'w') as sofia_fd:
                    sofia_fd.write(pformat(config))
                print('SignalWire addresses changed - importgateways')
            else:
                print('No change')
        else:
            print('No SignalWire gateway')
