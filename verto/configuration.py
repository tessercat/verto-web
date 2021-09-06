""" Verto app config request handler module. """
from django.conf import settings
from configuration.fsapi import ModuleConfigHandler, register_config_handler


class VertoConfigHandler(ModuleConfigHandler):
    """ Verto config request handler. """

    def get_config(self, request):
        """ Return rendered config. """
        template = 'verto/verto.conf.xml'
        context = {'port': settings.PORTS['verto']}
        return self.rendered(request, template, context)


register_config_handler('verto', VertoConfigHandler())
