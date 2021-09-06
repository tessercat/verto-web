""" Intercom app admin module. """
from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html
from intercom.models import (
    OutboundCallerId, Intercom,
    Extension, DidExtension,
    Bridge, OutboundExtension,
    Line, OutsideLine
)


@admin.register(OutboundCallerId)
class OutboundCallerIdAdmin(admin.ModelAdmin):
    """ OutboundCallerId model admin tweaks. """
    list_display = ('name', 'phone_number')


@admin.register(Intercom)
class IntercomAdmin(admin.ModelAdmin):
    """ Intercom model admin tweaks. """

    def uri_repr(self, obj):
        """ Return profile SIPS URI. """
        # pylint: disable=no-self-use
        return f'sips:{settings.PBX_HOSTNAME}:{obj.port}'

    uri_repr.short_description = 'URI'
    list_display = ('domain', 'uri_repr', 'default_outbound_caller_id')
    ordering = ('pk',)
    readonly_fields = ('port', 'domain', 'uri_repr')

    def has_add_permission(self, request):
        """ Disable add. """
        return False

    def has_delete_permission(self, request, obj=None):
        """ Disable delete. """
        return False


@admin.register(Extension)
class ExtensionAdmin(admin.ModelAdmin):
    """ Extension model admin tweaks. """

    def action_repr(self, obj):
        """ Return a representation of the action. """
        # pylint: disable=no-self-use
        action = obj.get_action()
        if action:
            return '%s %s' % (obj.get_action().__class__.__name__, action.name)
        return None

    action_repr.short_description = 'Action'

    exclude = ('channel',)
    list_display = (
        'extension_number',
        'intercom',
        'action_repr'
    )


@admin.register(DidExtension)
class DidExtensionAdmin(admin.ModelAdmin):
    """ DidExtension model admin tweaks. """
    list_display = ('did_number', 'extension')


@admin.register(Bridge)
class BridgeAdmin(admin.ModelAdmin):
    """ Bridge model admin tweaks. """

    def lines_link(self, obj):
        """ Return a link to the Bridge's Lines. """
        # pylint: disable=no-self-use
        count = obj.line_set.count()
        if count:
            url = '/admin/intercom/line/?q=%d' % obj.pk
            return format_html('<a href="%s">%d</a>' % (url, count))
        return None

    def outside_lines_link(self, obj):
        """ Return a link to the Bridge's OutsideLines. """
        # pylint: disable=no-self-use
        count = obj.outsideline_set.count()
        if count:
            url = '/admin/intercom/outsideline/?q=%d' % obj.pk
            return format_html('<a href="%s">%d</a>' % (url, count))
        return None

    lines_link.short_description = 'Intercom lines'
    outside_lines_link.short_description = 'Outside lines'

    # Add Line and OutsideLine links?
    list_display = ('name', 'extension', 'lines_link', 'outside_lines_link')


@admin.register(OutboundExtension)
class OutboundExtensionAdmin(admin.ModelAdmin):
    """ OutboundExtension model admin tweaks. """
    list_display = ('name', 'expression', 'gateway')


@admin.register(Line)
class LineAdmin(admin.ModelAdmin):
    """ Line model admin tweaks. """

    def bridges_count(self, obj):
        """ Return the number of Bridges the Line is in. """
        # pylint: disable=no-self-use
        count = obj.bridges.count()
        if count:
            return count
        return None

    def outbound_count(self, obj):
        """ Return the number of OutboundExtensions a Line has. """
        # pylint: disable=no-self-use
        count = obj.outbound_extensions.count()
        if count:
            return count
        return None

    bridges_count.short_description = 'Bridges'
    outbound_count.short_description = 'Outbound'

    exclude = ('registered',)
    list_display = (
        'name',
        'intercom',
        'extension',
        'bridges_count',
        'outbound_count',
        'outbound_caller_id',
        'registered'
    )
    search_fields = ['bridges__pk__exact']


@admin.register(OutsideLine)
class OutsideLineAdmin(admin.ModelAdmin):
    """ OutsideLine model admin tweaks. """

    def bridges_count(self, obj):
        """ Return the number of Bridges the Line is in. """
        # pylint: disable=no-self-use
        count = obj.bridges.count()
        if count:
            return count
        return None

    bridges_count.short_description = 'Bridges'
    list_display = (
        'note',
        'phone_number',
        'bridges_count',
        'gateway',
    )
    search_fields = ['bridges__pk__exact']
