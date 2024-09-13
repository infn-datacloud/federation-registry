"""Neomodel model of the Resource Provider (openstack, kubernetesapp..)."""
from neomodel import (
    ArrayProperty,
    BooleanProperty,
    RelationshipTo,
    StringProperty,
    StructuredNode,
    UniqueIdProperty,
    ZeroOrMore,
)

from fed_reg.auth_method.models import AuthMethod
from fed_reg.provider.enum import ProviderStatus


class Provider(StructuredNode):
    """Provider (openstack, kubernetesapp..).

    A Provider has a name which could not be unique, providers with
    same name must have different type; for example a site
    provides different providers with same name but one is an openstack instance
    the other is a kubernetes cluster.
    It has a list of maintainers, can be public or private.
    The provider status is used to notify users if the provider is available or not.
    It is divided into Regions (at least one).
    It allows authentication through multiple Identity Providers.
    It support multiple Projects.

    Attributes:
    ----------
        uid (int): Provider unique ID.
        description (str): Brief description.
        name (str): Provider name.
        type (str): Provider type.
        status (str | None): Provider status.
        is_public (bool): Public or private Provider.
        support_email (list of str): list of maintainers emails.
    """

    uid = UniqueIdProperty()
    description = StringProperty(default="")
    name = StringProperty(required=True)
    type = StringProperty(required=True)
    status = StringProperty(default=ProviderStatus.ACTIVE.value)
    is_public = BooleanProperty(default=False)
    support_emails = ArrayProperty(StringProperty(), default=[])

    projects = RelationshipTo(
        "fed_reg.project.models.Project",
        "BOOK_PROJECT_FOR_SLA",
        cardinality=ZeroOrMore,
    )
    regions = RelationshipTo(
        "fed_reg.region.models.Region", "DIVIDED_INTO", cardinality=ZeroOrMore
    )
    identity_providers = RelationshipTo(
        "fed_reg.identity_provider.models.IdentityProvider",
        "ALLOW_AUTH_THROUGH",
        cardinality=ZeroOrMore,
        model=AuthMethod,
    )

    def pre_delete(self):
        """Delete related identity providers, projects and regions.

        Remove the identity ptovider only if that idp points only to this provider.
        """
        for item in self.projects:
            item.delete()
        for item in self.regions:
            item.delete()
        for item in self.identity_providers:
            if len(item.providers) == 1:
                item.delete()
