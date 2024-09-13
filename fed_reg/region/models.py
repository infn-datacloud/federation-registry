"""Neomodel model of the Region owned by a Provider."""
from neomodel import (
    One,
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
    StructuredNode,
    UniqueIdProperty,
    ZeroOrMore,
    ZeroOrOne,
)


class Region(StructuredNode):
    """Region owned by a Provider.

    A Region is used to split a provider resources and limit projects access.
    A Region can have a specific geographical location and supplies
    different services (compute, block storage, network..).

    Attributes:
    ----------
        uid (uuid): AssociatedRegion unique ID.
        description (str): Brief description.
        name (str): Name of the Region in the Provider.
    """

    uid = UniqueIdProperty()
    description = StringProperty(default="")
    name = StringProperty(required=True)

    location = RelationshipTo(
        "fed_reg.location.models.Location", "LOCATED_AT", cardinality=ZeroOrOne
    )
    provider = RelationshipFrom(
        "fed_reg.provider.models.Provider", "DIVIDED_INTO", cardinality=One
    )
    services = RelationshipTo(
        "fed_reg.service.models.Service", "SUPPLY", cardinality=ZeroOrMore
    )

    def pre_delete(self):
        """Remove related services and location.

        Remove the location only if that location points only to this region.
        """
        for item in self.services:
            item.delete()
        item = self.location.single()
        if item and len(item.regions) == 1:
            item.delete()
