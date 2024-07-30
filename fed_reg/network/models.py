"""Neomodel model of the Virtual Machine Network owned by a Provider."""
from neomodel import (
    ArrayProperty,
    BooleanProperty,
    IntegerProperty,
    One,
    RelationshipFrom,
    StringProperty,
    StructuredNode,
    UniqueIdProperty,
)


class Network(StructuredNode):
    """Virtual Machine Network owned by a Provider.

    A VM Network is uniquely identified in the Provider by its uuid.
    It has a name and a set of parameters such as the MTU.
    A Network can be shared or private.
    When a Project has multiple private or public networks, it is mandatory
    to specify which is the default one.
    For VM using non public networks (is_router_external=False), to access to the VM,
    users need to use a Proxy. To use the Proxy they require the proxy host and the
    username to use to access.

    Attributes:
    ----------
        uid (int): Network unique ID.
        description (str): Brief description.
        name (str): Network name in the Provider.
        uuid (str): Network unique ID in the Provider
        is_shared (bool): Public or private Network.
        is_router_external (bool): Network with access to the outside.
        is_default (bool): Network to use as default.
        mtu (int | None): Metric transmission unit (B).
        proxy_host (str | None): Proxy IP address.
        proxy_user (str | None): Proxy username.
        tags (list of str): list of tags associated to this Network.
    """

    uid = UniqueIdProperty()
    description = StringProperty(default="")
    name = StringProperty(required=True)
    uuid = StringProperty(required=True)
    is_router_external = BooleanProperty(default=False)
    is_default = BooleanProperty(default=False)
    mtu = IntegerProperty()
    proxy_host = StringProperty()
    proxy_user = StringProperty()
    tags = ArrayProperty(StringProperty(), default=[])

    service = RelationshipFrom(
        "fed_reg.service.models.NetworkService",
        "AVAILABLE_NETWORK",
        cardinality=One,
    )


class PrivateNetwork(Network):
    """Virtual Machine Network owned by a Provider.

    Private networks are connected to only one Project.

    Attributes:
    ----------
        uid (int): Network unique ID.
        description (str): Brief description.
        name (str): Network name in the Provider.
        uuid (str): Network unique ID in the Provider
        is_shared (bool): Public or private Network.
        is_router_external (bool): Network with access to the outside.
        is_default (bool): Network to use as default.
        mtu (int | None): Metric transmission unit (B).
        proxy_host (str | None): Proxy IP address.
        proxy_user (str | None): Proxy username.
        tags (list of str): list of tags associated to this Network.
    """

    is_shared = BooleanProperty(default=False)

    project = RelationshipFrom(
        "fed_reg.project.models.Project",
        "CAN_USE_NETWORK",
        cardinality=One,
    )


class SharedNetwork(Network):
    """Virtual Machine Network owned by a Provider.

    Shared are available to all projects.

    Attributes:
    ----------
        uid (int): Network unique ID.
        description (str): Brief description.
        name (str): Network name in the Provider.
        uuid (str): Network unique ID in the Provider
        is_shared (bool): Public or private Network.
        is_router_external (bool): Network with access to the outside.
        is_default (bool): Network to use as default.
        mtu (int | None): Metric transmission unit (B).
        proxy_host (str | None): Proxy IP address.
        proxy_user (str | None): Proxy username.
        tags (list of str): list of tags associated to this Network.
    """

    is_shared = BooleanProperty(default=True)
