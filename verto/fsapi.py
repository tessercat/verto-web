""" Verto app fsapi request handler module. """
from uuid import UUID
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from verto.models import Client
from fsapi.views import FsapiHandler, register_fsapi_handler


class VertoLoginHandler(FsapiHandler):
    """ Handle verto client login events. """

    def __init__(self):
        super().__init__(
            action='verto_client_login',
        )

    def get_document(self, request):
        """ Process verto client login events and return "punt" on error.
        If the login is OK, set the Client object's connected timestamp.

        Assume that FreeSWITCH POSTs these events only on login success
        and therefore that it's safe to assume that a client object exists
        for the POSTed client_id and that it must be a UUID since the
        Client model enforces UUID client_id.

        Assume that if the POSTed session_id is not a UUID, that testing
        it against the expected value will catch the error since the
        Client model enforces UUID session_id.
        """
        template = 'verto/event.txt'
        client = Client.objects.get(client_id=request.POST['client_id'])
        if str(client.session_id) != request.POST['session_id']:
            self.admin_logger.error(
                'Session ID mismatch', extra={'request': request}
            )
            self.logger.info(
                'Session ID mismatch for client %s %s expected %s.',
                client, request.POST['session_id'], client.session_id
            )
            return self.rendered(request, template, {'response': 'punt'})
        # Punt if channel is full.
        client.connected = timezone.now()
        client.save()
        return self.rendered(request, template, {'response': 'ok'})


class VertoDisconnectHandler(FsapiHandler):
    """ Handle verto client disconnect events. """

    def __init__(self):
        super().__init__(
            action='verto_client_disconnect',
        )

    def get_document(self, request):
        """ Process verto client disconnect events and return "ok". If a
        client for the login username (client_id) is found, unset the
        client's connected timestamp. """
        template = 'verto/event.txt'
        client_id = request.POST['client_id'].split('@')[0]
        try:
            UUID(client_id, version=4)
        except ValueError as err:
            raise Http404 from err
        client = get_object_or_404(Client, client_id=client_id)
        client.connected = None
        client.save()
        return self.rendered(request, template, {'response': 'ok'})


register_fsapi_handler(VertoLoginHandler())
register_fsapi_handler(VertoDisconnectHandler())
