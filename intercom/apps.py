""" Intercom app config module. """
from django.apps import AppConfig


intercom_settings = {}


class IntercomConfig(AppConfig):
    """ Intercom app config. """
    # pylint: disable=import-outside-toplevel
    name = 'intercom'

    def config_action_names(self):
        """ Add action_names to settings. """
        # pylint: disable=no-self-use
        from intercom.models import Action

        action_names = []
        for subclass in Action.__subclasses__():
            action_names.append(subclass._meta.model_name)
        intercom_settings['action_names'] = action_names

    def config_dialplan_handlers(self):
        """ Configure dialplan handlers. """
        # pylint: disable=no-self-use
        from dialplan.fsapi import register_dialplan_handler
        from intercom.dialplan import (
            LineCallHandler,
            InboundCallHandler
        )
        from intercom.models import Intercom
        from sofia.models import Gateway

        for intercom in Intercom.objects.all():
            register_dialplan_handler(intercom.domain, LineCallHandler())
        for gateway in Gateway.objects.all():
            register_dialplan_handler(gateway.domain, InboundCallHandler())

    def config_directory_handlers(self):
        """ Configure directory handlers. """
        # pylint: disable=no-self-use
        from directory.fsapi import register_directory_handler
        from intercom.models import Intercom
        from intercom.directory import LineAuthHandler

        for intercom in Intercom.objects.all():
            register_directory_handler(intercom.domain, LineAuthHandler())

    def config_gateways(self):
        """ Add gateways to settings. """
        # pylint: disable=no-self-use
        from sofia.models import Gateway

        intercom_settings['gateways'] = list(
            Gateway.objects.order_by('priority')
        )

    def ready(self):
        """ Config on app ready. """
        import logging
        import sys
        from django.db.utils import OperationalError

        # Configure the intercom.
        self.config_action_names()
        try:
            self.config_gateways()
            self.config_dialplan_handlers()
            self.config_directory_handlers()
        except OperationalError:
            pass  # These fail when tables don't exist.

        # Log settings.
        logger = logging.getLogger('django.server')
        for key, value in intercom_settings.items():
            logger.info('%s %s %s', self.name, key, value)

        # Open ports.
        if sys.argv[-1] == 'project.asgi:application':
            from common import firewall
            from intercom.models import Intercom

            for intercom in Intercom.objects.all():
                firewall.accept(
                    'tcp',
                    intercom.port,
                    intercom.port,
                )
                logger.info(
                    '%s opened tcp %s',
                    self.name, intercom.port
                )
