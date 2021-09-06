""" Intercom dialplan app dialplan request handler module. """
from django.http import Http404
from django.shortcuts import get_object_or_404
from dialplan.fsapi import DialplanHandler
from intercom.models import Extension, DidExtension, Line, get_e164


class LineCallHandler(DialplanHandler):
    """ Line call dialplan request handler. """

    # Handle 404 with an annotation.
    def get_dialplan(self, request, context):
        """ Return Line Extension/Matcher template/context. """

        # Get the dialed number.
        dest_number = request.POST.get('Caller-Destination-Number')
        if not dest_number:
            raise Http404

        # Get the calling Line.
        username = request.POST.get('variable_user_name')
        if not username:
            raise Http404
        caller = get_object_or_404(Line, username=username)

        # Try Extensions.
        try:

            # Extension.
            extension = Extension.objects.get(
                intercom__domain=context,
                extension_number=dest_number
            )
            action = extension.get_action()
            if not action:
                raise Http404
            template = action.template
            context_data = {
                'context': context,
                'dest_number': extension.extension_number,
                'caller': caller,
                'extension': extension,
                'action': action,
            }
            return self.rendered(request, template, context_data)
        except Extension.DoesNotExist:
            pass

        # Try DidExtensions and OutboundExtensions.
        full_number = get_e164(dest_number)
        if not full_number:
            raise Http404
        did_extensions = DidExtension.objects.all()
        for outbound_ext in caller.outbound_extensions.all():
            if outbound_ext.matches(full_number):

                # Route to another Intercom via DidExtension.
                for did_extension in did_extensions:
                    if did_extension.did_number == full_number:
                        extension = did_extension.extension
                        if not extension:
                            raise Http404
                        action = extension.get_action()
                        if not action:
                            raise Http404
                        template = action.template
                        context_data = {
                            'context': context,
                            'dest_number': extension.extension_number,
                            'caller': caller,
                            'extension': extension,
                            'action': action,
                        }
                        return self.rendered(request, template, context_data)

                # Route via Gateways.
                template = outbound_ext.template
                context_data = {
                    'context': context,
                    'dest_number': dest_number,
                    'caller': caller,
                    'gateway': outbound_ext.gateway
                }
                return self.rendered(request, template, context_data, True)

        # No Extension, no DidExtension, no OutboundExtension.
        raise Http404


class InboundCallHandler(DialplanHandler):
    """ Inbound call dialplan request handler. """

    # Handle 404 with an annotation.
    def get_dialplan(self, request, context):
        """ Return template/context. """

        # Called number is the Gateway's registration user.
        dest_number = request.POST.get('Caller-Destination-Number')
        if not dest_number:
            raise Http404
        # Check that dest number matches gateway?

        # Caller ID
        caller = {
            'name': request.POST.get('Caller-Caller-ID-Name'),
            'number': request.POST.get('Caller-Caller-ID-Number')
        }

        # SIP to user is the full number.
        did_number = request.POST.get('variable_sip_to_user')
        try:
            did_extension = DidExtension.objects.get(did_number=did_number)
        except DidExtension.DoesNotExist:
            pass  # Write an error log / admin email.
        extension = did_extension.extension
        action = extension.get_action()
        if not action:
            raise Http404

        # Action extension.
        template = action.template
        context_data = {
            'context': context,
            'dest_number': dest_number,
            'caller': caller,
            'extension': extension,
            'action': action,
        }
        return self.rendered(request, template, context_data)
