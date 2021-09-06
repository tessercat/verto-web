""" Sofia app config request handler module. """
from django.conf import settings
from django.shortcuts import get_object_or_404
from configuration.fsapi import ModuleConfigHandler, register_config_handler
from intercom.models import Intercom
from sofia.models import Gateway


class SofiaConfigHandler(ModuleConfigHandler):
    """ Sofia profile config request handler. """

    def get_config(self, request):
        """ Return rendered config. """
        # self.logger.info(request.POST.dict())
        domain = request.POST.get('profile')
        if domain:

            # The profile thread has requested its own configuration.
            try:
                intercom = Intercom.objects.get(domain=domain)
                template = 'sofia/intercom.conf.xml'
                context = {'intercom': intercom}
            except Intercom.DoesNotExist:
                gateway = get_object_or_404(Gateway, domain=domain)
                template = 'sofia/gateway.conf.xml'
                context = {
                    'gateway': gateway,
                    'hostname': settings.PBX_HOSTNAME
                }
            return self.rendered(request, template, context)

        # No profile specified in POST. Return all profiles.
        template = 'sofia/sofia.conf.xml'
        context = {
            'intercoms': Intercom.objects.all(),
            'gateways': Gateway.objects.all()
        }
        return self.rendered(request, template, context)


register_config_handler('sofia', SofiaConfigHandler())
