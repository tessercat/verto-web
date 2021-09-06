""" Intercom app URL config. """
from django.urls import path
from intercom.views import IndexView, ClientView, SessionView


urlpatterns = [
    path(
        '',
        IndexView.as_view(),
        name='pbx-intercom-index'
    ),
    path(
        '<uuid:channel_id>',
        ClientView.as_view(),
        name='pbx-intercom-client'
    ),
    path(
        '<uuid:channel_id>/session',
        SessionView.as_view(),
        name='pbx-intercom-session'
    ),
]
