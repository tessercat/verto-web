""" Directory request handler module. """
import logging
from django.http import Http404
from fsapi.views import Handler, FsapiHandler, register_fsapi_handler


directory_handlers = {}


def register_directory_handler(domain, handler):
    """ Add a directory handler to the registry."""
    directory_handlers[domain] = handler
    logging.getLogger('django.server').info(
        'directory %s %s', domain, handler
    )


class DirectoryHandler(Handler):
    """ Directory handler abstract class. """

    def get_directory(self, request, domain):
        """ Return rendered directory. """
        raise NotImplementedError


class DirectorySectionHandler(FsapiHandler):
    """ Handler for all directory requests. """

    def __init__(self):
        super().__init__(
            section='directory',
        )

    def get_document(self, request):
        """ Return directory document. """
        domain = request.POST.get('key_value')
        if not domain:
            raise Http404
        handler = directory_handlers.get(domain)
        if not handler:
            self.logger.info('No directory handler for %s', domain)
            raise Http404
        return handler.get_directory(request, domain)


register_fsapi_handler(DirectorySectionHandler())
