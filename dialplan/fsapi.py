""" Dialplan request handler module. """
import logging
from django.http import Http404
from fsapi.views import Handler, FsapiHandler, register_fsapi_handler


dialplan_handlers = {}


def register_dialplan_handler(context, handler):
    """ Add a dialplan handler to the registry."""
    dialplan_handlers[context] = handler
    logging.getLogger('django.server').info(
        'dialplan %s %s',
        context, handler
    )


class DialplanHandler(Handler):
    """ Abstract dialplan handler. """

    def get_dialplan(self, request, context):
        """ Return rendered dialplan. """
        raise NotImplementedError


class DialplanSectionHandler(FsapiHandler):
    """ Handler for all dialplan requests. """

    def __init__(self):
        super().__init__(
            section='dialplan',
        )

    def get_document(self, request):
        """ Return dialplan document. """
        context = request.POST.get('Caller-Context')
        if not context:
            raise Http404
        handler = dialplan_handlers.get(context)
        if not handler:
            self.logger.info('No dialplan handler for %s', context)
            raise Http404
        return handler.get_dialplan(request, context)


register_fsapi_handler(DialplanSectionHandler())
