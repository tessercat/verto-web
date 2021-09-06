""" Intercom app template tags module. """
from django import template
from django.http import Http404
from intercom.apps import intercom_settings
from intercom.models import get_e164


register = template.Library()


def outbound_dialstring(dest_number, gateways, cid):
    """ Return a dialstring that bridges to the gateways.

    Caller ID cid is a dict of name/number. """

    # Normalize the dialed number.
    full_number = get_e164(dest_number)
    if not full_number:
        raise Http404

    dialstrings = []
    dialstring = '[%s,%s]sofia/gateway/%s/%s'
    for gateway in gateways:
        dialstrings.append(dialstring % (
            'origination_caller_id_name=%s' % cid['name'],
            'origination_caller_id_number=%s' % cid['number'],
            gateway.domain,
            full_number
        ))
    return '|'.join(dialstrings)


@register.simple_tag
def get_dialstring(caller, dest_number, gateway):
    """ Return the dialstring for the outbound call. """
    if gateway:
        gateways = (gateway,)
    else:
        gateways = intercom_settings['gateways']

    cid_obj = None
    if caller.outbound_caller_id:
        cid_obj = caller.outbound_caller_id
    elif caller.intercom.default_outbound_caller_id:
        cid_obj = caller.intercom.default_outbound_caller_id
    if cid_obj:
        outbound_cid = {'name': cid_obj.name, 'number': cid_obj.phone_number}
    else:
        outbound_cid = {'name': caller.name, 'number': caller.username}
    return outbound_dialstring(dest_number, gateways, outbound_cid)
