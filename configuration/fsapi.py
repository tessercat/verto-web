""" Configuration request handler module. """
import logging
from django.http import Http404
from fsapi.views import Handler, FsapiHandler, register_fsapi_handler


module_config_handlers = {}


def register_config_handler(module, handler):
    """ Add a module configuration handler to the registry."""
    module_config_handlers[module] = handler
    logging.getLogger('django.server').info(
        'configuration %s %s',
        module, handler
    )


class ModuleConfigHandler(Handler):
    """ Module configuration handler abstract class. """

    def get_config(self, request):
        """ Return rendered config. """
        raise NotImplementedError


class ConfigSectionHandler(FsapiHandler):
    """ Handler for all configuration requests. """

    def __init__(self):
        super().__init__(
            section='configuration',
        )

    def get_document(self, request):
        """ Return config document. """
        key_value = request.POST.get('key_value')
        if not key_value:
            raise Http404
        module = key_value.split('.')[0]
        handler = module_config_handlers.get(module)
        if not handler:
            self.logger.info('No configuration handler for %s', module)
            raise Http404
        return handler.get_config(request)


register_fsapi_handler(ConfigSectionHandler())
