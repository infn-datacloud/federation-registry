"""Neomodel models of the Service supplied by a Provider on a specific Region."""
from neomodel import (
    One,
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
    StructuredNode,
    UniqueIdProperty,
    ZeroOrMore,
)


class Service(StructuredNode):
    """Service supplied by a Provider on a specific Region.

    Common attributes to all service types.
    Any service is accessible through an endpoint, which is unique in the DB.

    TODO: function using cypher to retrieve IDPs?

    Attributes:
    ----------
        uid (int): Service unique ID.
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        type (str): Service type.
        name (str): Service name.
    """

    uid = UniqueIdProperty()
    description = StringProperty(default="")
    endpoint = StringProperty(required=True)
    type = StringProperty(required=True)
    name = StringProperty(required=True)

    region = RelationshipFrom("fed_reg.region.models.Region", "SUPPLY", cardinality=One)


class BlockStorageService(Service):
    """Service managing Block Storage resources.

    A Block Storage Service, for each project, support a set of quotas managing the
    block storage resources.

    Attributes:
    ----------
        uid (int): Service unique ID.
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        type (str): Service type.
        name (str): Service name.
    """

    quotas = RelationshipFrom(
        "fed_reg.quota.models.BlockStorageQuota", "APPLY_TO", cardinality=ZeroOrMore
    )


class ComputeService(Service):
    """Service managing Compute resources.

    A Compute Service, for each project, support a set of quotas managing the block
    storage resources. A Compute Service provides public and private Flavors and Images.

    Attributes:
    ----------
        uid (int): Service unique ID.
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        type (str): Service type.
        name (str): Service name.
    """

    flavors = RelationshipTo(
        "fed_reg.flavor.models.Flavor",
        "AVAILABLE_VM_FLAVOR",
        cardinality=ZeroOrMore,
    )
    images = RelationshipTo(
        "fed_reg.image.models.Image",
        "AVAILABLE_VM_IMAGE",
        cardinality=ZeroOrMore,
    )
    quotas = RelationshipFrom(
        "fed_reg.quota.models.ComputeQuota", "APPLY_TO", cardinality=ZeroOrMore
    )


class IdentityService(Service):
    """Service managing user access to the Provider.

    Attributes:
    ----------
        uid (int): Service unique ID.
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        type (str): Service type.
        name (str): Service name.
    """


class NetworkService(Service):
    """Service managing Network resources.

    A Network Service provides public and private Networks.

    Attributes:
    ----------
        uid (int): Service unique ID.
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        type (str): Service type.
        name (str): Service name.
    """

    networks = RelationshipTo(
        "fed_reg.network.models.Network",
        "AVAILABLE_NETWORK",
        cardinality=ZeroOrMore,
    )
    quotas = RelationshipFrom(
        "fed_reg.quota.models.NetworkQuota", "APPLY_TO", cardinality=ZeroOrMore
    )


class ObjectStoreService(Service):
    """Service managing Object Storage resources.

    An Object Storage Service, for each project, support a set of quotas managing the
    object storage resources.

    Attributes:
    ----------
        uid (int): Service unique ID.
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        type (str): Service type.
        name (str): Service name.
    """

    quotas = RelationshipFrom(
        "fed_reg.quota.models.ObjectStoreQuota", "APPLY_TO", cardinality=ZeroOrMore
    )
