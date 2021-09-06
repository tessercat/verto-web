""" Intercom app directory request handler module. """
from uuid import UUID
from django.http import Http404
from django.shortcuts import get_object_or_404
from directory.fsapi import DirectoryHandler
from intercom.models import Intercom, Line
from verto.models import Client


class LineAuthHandler(DirectoryHandler):
    """ Handle Line auth requests. """

    def get_directory(self, request, domain):
        """ Return template/context to auth a Line registration. """

        # Reject directory gateway requests.
        purpose = request.POST.get('purpose')
        if purpose and purpose == 'gateways':
            # 1.10.6 does this when <domain> is configured,
            # even when parse=false.
            raise Http404

        # Send the line-auth template.
        username = request.POST.get('user')
        if not username:
            raise Http404
        intercom = get_object_or_404(Intercom, domain=domain)
        line = get_object_or_404(Line, username=username, intercom=intercom)
        template = 'intercom/line-auth.xml'
        context = {'line': line}
        return self.rendered(request, template, context)


class ClientAuthHandler(DirectoryHandler):
    """ Handle a verto channel auth request. """

    @staticmethod
    def get_client(request):
        """ Return the Client object to auth. """
        client_id = request.POST.get('user')
        if not client_id:
            raise Http404
        try:
            UUID(client_id, version=4)
        except ValueError as err:
            raise Http404 from err
        return get_object_or_404(Client, client_id=client_id)

    def get_directory(self, request, domain):
        """ Return template/context for channel auth. """
        client = self.get_client(request)
        if hasattr(client.channel, 'extension'):
            template = 'intercom/client-auth.xml'
            context = {'client': client}
            return self.rendered(request, template, context)
        raise Http404
