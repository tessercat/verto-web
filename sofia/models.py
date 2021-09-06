""" Sofia app models module. """
from django.db import models


class SofiaProfile(models.Model):
    """ A generic sofia profile. """
    port = models.IntegerField(
        unique=True
    )
    domain = models.SlugField(
        max_length=50,
        unique=True
    )

    def __str__(self):
        return self.domain


class Gateway(SofiaProfile):
    """ A SofiaProfile for gateway calls. """
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    proxy = models.CharField(max_length=50)
    realm = models.CharField(max_length=50)
    priority = models.PositiveSmallIntegerField()
    # JSON params field?
    # Datetime registered field and listen for events?


class AclAddress(models.Model):
    """ An IP address for a Gateway. """

    class Meta:
        verbose_name = 'ACL address'
        verbose_name_plural = 'ACL addresses'

    address = models.GenericIPAddressField()
    gateway = models.ForeignKey(
        Gateway,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.gateway} - {self.address}'
