from neomodel import (
    One,
    RelationshipFrom,
    StringProperty,
    StructuredNode,
    UniqueIdProperty,
    ZeroOrMore,
)


class Service(StructuredNode):
    """Service class.

    A Service manages a specific amount of resource types
    defined by a set of quotas and belonging to an SLA.
    It is accessible through an endpoint.

    TODO: Authentication
    through IAM can be accepted. It can accept multiple
    authentication methods. It can be public or private.

    Attributes:
        uid (int): Service unique ID.
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        type (str): Service type.
    """

    uid = UniqueIdProperty()
    description = StringProperty(default="")
    endpoint = StringProperty(unique_index=True, required=True)
    type = StringProperty(required=True)
    name = StringProperty(required=True)

    provider = RelationshipFrom("..provider.models.Provider", "SUPPLY", cardinality=One)


class NovaService(Service):
    quotas = RelationshipFrom(
        "..quota.models.NovaQuota", "APPLY_TO", cardinality=ZeroOrMore
    )


class CinderService(Service):
    quotas = RelationshipFrom(
        "..quota.models.CinderQuota", "APPLY_TO", cardinality=ZeroOrMore
    )


class KeystoneService(Service):
    pass
