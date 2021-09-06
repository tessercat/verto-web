""" Intercom app template tags module. """
from django.conf import settings
from django import template
from intercom.apps import intercom_settings
from intercom.models import Line
from intercom.templatetags.outbound_extras import outbound_dialstring


register = template.Library()


@register.simple_tag
def get_dialstring(caller, extension, action):
    """ Return the dialstring for the bridge template. """

    # Local/outbound caller ID
    local_cid = {}
    outbound_cid = {}
    if isinstance(caller, Line):
        local_cid['name'] = caller.name
        local_cid['number'] = caller.username
        if caller.extension:
            local_cid['number'] = caller.extension.extension_number
        intercom_cid = extension.intercom.default_outbound_caller_id
        if intercom_cid:
            outbound_cid['name'] = intercom_cid.name
            outbound_cid['number'] = intercom_cid.phone_number
        else:
            outbound_cid = local_cid
    else:
        # For inbound calls, the dialplan sends name/number dict.
        local_cid = caller
        outbound_cid = caller

    # Generate dialstring.
    dialstrings = []

    # Call other Lines.
    tpl = '[%s,%s]${sofia_contact(%s@%s)}'
    for line in action.line_set.all():
        if line == caller:
            continue
        dialstrings.append(tpl % (
            'origination_caller_id_name=%s' % local_cid['name'],
            'origination_caller_id_number=%s' % local_cid['number'],
            line.username,
            settings.PBX_HOSTNAME
        ))

    # Call other OutsideLines.
    for outside_line in action.outsideline_set.all():
        if isinstance(caller, dict):
            if caller['number'] == outside_line.phone_number:
                continue
        if outside_line.gateway:
            gateways = (outside_line.gateway,)
        else:
            gateways = intercom_settings['gateways']
        dialstrings.append(outbound_dialstring(
            outside_line.phone_number, gateways, outbound_cid
        ))

    # Return the complete dialstring.
    return ':_:'.join(dialstrings)
