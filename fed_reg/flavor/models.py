"""Neomodel model of the Virtual Machine Flavor owned by a Provider."""
from neomodel import (
    BooleanProperty,
    IntegerProperty,
    OneOrMore,
    RelationshipFrom,
    StringProperty,
    StructuredNode,
    UniqueIdProperty,
)


class Flavor(StructuredNode):
    """Virtual Machine Flavor owned by a Provider.

    A VM Flavor is uniquely identified in the Provider by its uuid.
    It has a name and a set of parameters such as number of CPUs and GPUs,
    fixed RAM and disk size and more.
    A Flavor can be public or private.
    If it is public it has no relationships, otherwise it is connected to
    all and only the Projects who have access.

    Attributes:
    ----------
        uid (str): Flavor unique ID.
        description (str): Brief description.
        name (str): Flavor name in the Provider.
        uuid (str): Flavor unique ID in the Provider
        disk (int): Reserved disk size (GiB)
        ram (int): Reserved RAM (MiB)
        vcpus (int): Number of Virtual CPUs.
        swap (int): Swap size (GiB).
        ephemeral (int): Ephemeral disk size (GiB).
        infiniband (bool): MPI - parallel multi-process enabled.
        gpus (int): Number of GPUs.
        gpu_model (str | None): GPU model name.
        gpu_vendor (str | None): Name of the GPU vendor.
        local_storage (str | None): Local storage presence.
    """

    uid = UniqueIdProperty()
    description = StringProperty(default="")
    name = StringProperty(required=True)
    uuid = StringProperty(required=True)
    disk = IntegerProperty(default=0)
    is_public = BooleanProperty(default=True)
    ram = IntegerProperty(default=0)
    vcpus = IntegerProperty(default=0)
    swap = IntegerProperty(default=0)
    ephemeral = IntegerProperty(default=0)
    infiniband = BooleanProperty(default=False)
    gpus = IntegerProperty(default=0)
    gpu_model = StringProperty()
    gpu_vendor = StringProperty()
    local_storage = StringProperty()

    services = RelationshipFrom(
        "fed_reg.service.models.ComputeService",
        "AVAILABLE_VM_FLAVOR",
        cardinality=OneOrMore,
    )


class PrivateFlavor(Flavor):
    """Virtual Machine Flavor owned by a Provider.

    A Private Flavor can be used by one or multiple projects. At least one project must
    point to this item.

    Attributes:
    ----------
        uid (str): Flavor unique ID.
        description (str): Brief description.
        name (str): Flavor name in the Provider.
        uuid (str): Flavor unique ID in the Provider
        disk (int): Reserved disk size (GiB)
        is_public (bool): Public or private Flavor.
        ram (int): Reserved RAM (MiB)
        vcpus (int): Number of Virtual CPUs.
        swap (int): Swap size (GiB).
        ephemeral (int): Ephemeral disk size (GiB).
        infiniband (bool): MPI - parallel multi-process enabled.
        gpus (int): Number of GPUs.
        gpu_model (str | None): GPU model name.
        gpu_vendor (str | None): Name of the GPU vendor.
        local_storage (str | None): Local storage presence.
    """

    is_public = BooleanProperty(default=False)

    projects = RelationshipFrom(
        "fed_reg.project.models.Project",
        "CAN_USE_VM_FLAVOR",
        cardinality=OneOrMore,
    )


class SharedFlavor(Flavor):
    """Virtual Machine Flavor owned by a Provider.

    All projects have access to public flavors.

    Attributes:
    ----------
        uid (str): Flavor unique ID.
        description (str): Brief description.
        name (str): Flavor name in the Provider.
        uuid (str): Flavor unique ID in the Provider
        disk (int): Reserved disk size (GiB)
        is_public (bool): Public or private Flavor.
        ram (int): Reserved RAM (MiB)
        vcpus (int): Number of Virtual CPUs.
        swap (int): Swap size (GiB).
        ephemeral (int): Ephemeral disk size (GiB).
        infiniband (bool): MPI - parallel multi-process enabled.
        gpus (int): Number of GPUs.
        gpu_model (str | None): GPU model name.
        gpu_vendor (str | None): Name of the GPU vendor.
        local_storage (str | None): Local storage presence.
    """

    is_public = BooleanProperty(default=True)
