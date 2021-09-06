""" Intercom app admin module. """
from django.contrib import admin
from sofia.models import Gateway, AclAddress


@admin.register(Gateway)
class GatewayAdmin(admin.ModelAdmin):
    """ Gateway model admin tweaks. """
    exclude = ('password',)
    list_display = ('domain', 'port', 'priority')
    ordering = ('priority',)

    def has_add_permission(self, request):
        """ Disable add. """
        return False

    def has_change_permission(self, request, obj=None):
        """ Disable change. """
        return False

    def has_delete_permission(self, request, obj=None):
        """ Disable delete. """
        return False


@admin.register(AclAddress)
class AclAddressAdmin(admin.ModelAdmin):
    """ AclAddress model admin tweaks. """
    list_display = ('address', 'gateway')

    def has_add_permission(self, request):
        """ Disable add. """
        return False

    def has_change_permission(self, request, obj=None):
        """ Disable change. """
        return False

    def has_delete_permission(self, request, obj=None):
        """ Disable delete. """
        return False
