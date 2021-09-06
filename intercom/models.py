""" Intercom app models module. """
import re
from django.db import models
from intercom.apps import intercom_settings
from sofia.models import SofiaProfile, Gateway


def get_e164(number):
    """ Return the full E.164 phone number or None. """
    if re.fullmatch(r'\+1\d{10}', number):
        return number
    if re.fullmatch(r'1\d{10}', number):
        return '+%s' % number
    if re.fullmatch(r'\d{10}', number):
        return '+1%s' % number
    return None


class OutboundCallerId(models.Model):
    """ An ITSP-verified calling name/number to send out Gateways. """

    name = models.CharField(
        max_length=50
    )
    phone_number = models.CharField(
        max_length=50
    )

    def __str__(self):
        return f'{self.name} {self.phone_number}'


class Intercom(SofiaProfile):
    """ A SofiaProfile for intercom calls.

    Calls through Gateways present OutboundCallerId for outbound calls unless
    via OutboundExtensions and overridden by a Line. """

    default_outbound_caller_id = models.ForeignKey(
        OutboundCallerId,
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )


class Extension(models.Model):
    """ An Intercom's numbered dialplan extension.

    Action objects of various types reference Extensions. The get_action
    method returns the Action object that refrences a particular Extension
    object, if any. """

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='%(app_label)s_%(class)s_is_unique',
                fields=['extension_number', 'intercom']
            ),
        ]
        verbose_name = 'Intercom extension'
        verbose_name_plural = 'Intercom extensions'

    def get_action(self):
        """ Return the Extension's Action subtype or None. """
        if hasattr(self, 'action'):
            action = getattr(self, 'action')
            for name in intercom_settings['action_names']:
                if hasattr(action, name):
                    return getattr(action, name)
        return None

    extension_number = models.CharField(max_length=50)
    intercom = models.ForeignKey(
        Intercom,
        on_delete=models.CASCADE
    )
    voicemail = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.extension_number} ({self.intercom})'


class DidExtension(models.Model):
    """ A DID number and an Extension to call when the dialplan receives a
    call to the DID number through a Gateway. """

    class Meta:
        verbose_name = 'DID extension'
        verbose_name_plural = 'DID extensions'

    did_number = models.CharField(
        unique=True,
        max_length=50,
    )
    extension = models.ForeignKey(
        Extension,
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return f'{self.did_number} {self.extension}'


class Action(models.Model):
    """ A concrete named Extension dialplan action.

    Meant to be subclassed.

    The intercom.apps module enumerates subclasses on app ready, and Extension
    objects provide a get_action method so that dialplan handlers can retrieve
    and process the subclassed action object. """

    template = None

    name = models.CharField(max_length=50)
    extension = models.OneToOneField(
        Extension,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'{self.name} {self.extension}'


class Bridge(Action):
    """ An Action to call the Lines and OutsideLines that reference it. """

    class Meta:
        verbose_name = 'Line bridge'
        verbose_name_plural = 'Line bridges'

    template = 'intercom/bridge.xml'


class OutboundExtension(models.Model):
    """ A combined regular expression and dialplan action.

    Lines call external numbers directly via OutboundExtensions.

    The dialplan routes calls to the Gateway, if configured, or to common
    Gateways if not. No failover if configured.

    The dialplan sends the calling Line's OutboundCallerId, if configured,
    or the Intercom's if not. """

    def matches(self, full_number):
        """ Return True on full-number match. """
        if re.fullmatch(self.expression, full_number):
            return True
        return False

    template = 'intercom/outbound.xml'

    name = models.CharField(max_length=50)
    expression = models.CharField(max_length=50)
    gateway = models.ForeignKey(
        Gateway,
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.name


class Line(models.Model):
    """ A unique username/password registration for the host domain.

    Lines can call any of the Intercom's Extensions.

    Lines receive calls when any of the Bridges receive calls.

    Lines call through Gateways via OutboundExtensions, if configured.

    The Line name is used as caller ID name when calling other Intercom
    Extensions, and the Extension number is caller ID number.

    Eventually, add a Voicemail action. When calling a Voicemail action
    Extension, the Line automatically manages its Extension's voicemail.

    When dialing out via OutboundExtensions, the dialplan sends the
    OutboundCallerID, if configured, or the Intercom's default if not.

    Lines can also call through Gateways by calling a Bridge with
    OutsideLines, but the dialplan ignores the OutboundCallerId. """

    class Meta:
        verbose_name = 'Intercom line'
        verbose_name_plural = 'Intercom lines'

    name = models.CharField(max_length=15)
    username = models.SlugField(
        unique=True,
        max_length=50,
    )
    password = models.CharField(max_length=50)
    intercom = models.ForeignKey(
        Intercom,
        on_delete=models.CASCADE
    )
    extension = models.ForeignKey(
        Extension,
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    bridges = models.ManyToManyField(
        Bridge,
        blank=True,
    )
    outbound_extensions = models.ManyToManyField(
        OutboundExtension,
        blank=True,
    )
    outbound_caller_id = models.ForeignKey(
        OutboundCallerId,
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    registered = models.DateTimeField(
        blank=True,
        null=True,
    )

    def __str__(self):
        return f'{self.name} ({self.intercom})'


class OutsideLine(models.Model):
    """ An external phone number.

    The dialplan routes calls to the Gateway, if configured, or to common
    Gateways if not. No failover if configured.

    The dialplan always sends the Intercom's OutboundCallerId and ignores a
    calling Line's OutboundCallerId. """

    note = models.CharField(
        max_length=50,
    )
    phone_number = models.CharField(
        unique=True,
        max_length=50,
    )
    bridges = models.ManyToManyField(
        Bridge,
        blank=True,
    )
    gateway = models.ForeignKey(
        Gateway,
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return f'{self.note} {self.phone_number}'
