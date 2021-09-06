""" Extension app views module. """
from datetime import timedelta
from uuid import UUID
from django.conf import settings
from django.http import Http404, HttpResponseForbidden, JsonResponse
from django.utils import timezone
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView, BaseDetailView
from intercom.apps import intercom_settings
from intercom.models import Extension
from verto.models import Channel, Client


class IndexView(TemplateView):
    """ Intercom app index view. """
    template_name = 'intercom/index.html'

    def get_context_data(self, **kwargs):
        """ Insert data into template context. """
        context = super().get_context_data(**kwargs)
        context['title'] = 'Directory'
        context['css'] = intercom_settings.get('css')
        context['extensions'] = Extension.objects.filter(
            public=True,
            channel__isnull=False,
            action__isnull=False
        )
        return context


class ClientView(DetailView):
    """ Channel client view. """
    model = Channel
    slug_field = 'channel_id'
    slug_url_kwarg = 'channel_id'
    template_name = 'intercom/client.html'

    def get_context_data(self, **kwargs):
        """ Insert data into template context. """
        context = super().get_context_data(**kwargs)
        if not hasattr(self.object, 'extension'):
            raise Http404
        extension = self.object.extension
        action = extension.get_action()
        if not action:
            raise Http404
        context['title'] = 'Call %s' % action.name
        context['stun_port'] = settings.PORTS['stun']
        context['css'] = intercom_settings.get('css')
        context['adapter'] = intercom_settings.get('adapter')
        context['client'] = intercom_settings.get('client')
        return context


class SessionView(BaseDetailView):
    """ Channel client session registration view. """
    model = Channel
    slug_field = 'channel_id'
    slug_url_kwarg = 'channel_id'

    def get_context_data(self, **kwargs):
        """ Return clientId and password for the sessionId in request args.

        Raise 404 if a client exists for the session but the session is
        expired, or return None to raise 403 for all other errors.

        Return a dict of clientId and password for an existing, unexpired
        session, or from a new client whose session expires in two weeks.
        """
        session_id = self.request.GET.get('sessionId')
        if not session_id:
            return None
        try:
            UUID(session_id, version=4)
        except ValueError:
            return None
        try:
            client = Client.objects.get(session_id=session_id)
            if client.channel != self.object:
                return None
            if client.created + timedelta(days=14) < timezone.now():
                raise Http404
        except Client.DoesNotExist:
            client = Client.objects.create(
                channel=self.object,
                session_id=session_id
            )
        return {
            'sessionId': str(client.session_id),
            'clientId': str(client.client_id),
            'password': str(client.password)
        }

    def render_to_response(self, context):
        """ Return context as JSON response or 403. """
        # pylint: disable=no-self-use
        if not context:
            return HttpResponseForbidden()
        return JsonResponse(context)
