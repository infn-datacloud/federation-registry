"""Neomodel model of the Project owned by a Provider."""
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

from fed_reg.flavor.models import PublicFlavor
from fed_reg.image.models import Image
from fed_reg.network.models import Network
from fed_reg.service.enum import ServiceType


class Project(StructuredNode):
    """Project owned by a Provider.

    A project/tenant/namespace is uniquely identified in the
    Provider by its uuid.
    It has a name and can access all public flavors, images
    and networks plus the private flavors, images and networks.
    It has a set of quotas limiting the resources it can use on
    a specific service of the hosting Provider.
    A project should always be pointed by an SLA.

    Attributes:
    ----------
        uid (uuid): AssociatedProject unique ID.
        description (str): Brief description.
        name (str): Name of the project in the Provider.
        uuid (uuid): Project Unique ID in the Provider.
    """

    uid = UniqueIdProperty()
    description = StringProperty(default="")
    name = StringProperty(required=True)
    uuid = StringProperty(required=True)

    sla = RelationshipFrom(
        "fed_reg.sla.models.SLA",
        "REFER_TO",
        cardinality=ZeroOrOne,
    )
    quotas = RelationshipTo(
        "fed_reg.quota.models.Quota",
        "USE_SERVICE_WITH",
        cardinality=ZeroOrMore,
    )
    provider = RelationshipFrom(
        "fed_reg.provider.models.Provider",
        "BOOK_PROJECT_FOR_SLA",
        cardinality=One,
    )
    private_flavors = RelationshipTo(
        "fed_reg.flavor.models.PrivateFlavor",
        "CAN_USE_VM_FLAVOR",
        cardinality=ZeroOrMore,
    )
    private_images = RelationshipTo(
        "fed_reg.image.models.Image",
        "CAN_USE_VM_IMAGE",
        cardinality=ZeroOrMore,
    )
    private_networks = RelationshipTo(
        "fed_reg.network.models.Network",
        "CAN_USE_NETWORK",
        cardinality=ZeroOrMore,
    )

    query_prefix = """
        MATCH (p:Project)
        WHERE (elementId(p)=$self)
        MATCH (p)-[:`USE_SERVICE_WITH`]-(q)
        """

    def public_flavors(self) -> list[PublicFlavor]:
        """list public flavors this project can access.

        Make a cypher query to retrieve all public flavors this project can access.
        """
        results, _ = self.cypher(
            f"""
                {self.query_prefix}
                WHERE q.type = "{ServiceType.COMPUTE.value}"
                MATCH (q)-[:`APPLY_TO`]-(s)
                MATCH (s)-[:`AVAILABLE_VM_FLAVOR`]->(u:PublicFlavor)
                RETURN u
            """
        )
        return [PublicFlavor.inflate(row[0]) for row in results]

    def public_images(self) -> list[Image]:
        """list public images this project can access.

        Make a cypher query to retrieve all public images this project can access.
        """
        results, _ = self.cypher(
            f"""
                {self.query_prefix}
                WHERE q.type = "{ServiceType.COMPUTE.value}"
                MATCH (q)-[:`APPLY_TO`]-(s)
                MATCH (s)-[:`AVAILABLE_VM_IMAGE`]->(u:Image)
                WHERE u.is_public = True
                RETURN u
            """
        )
        return [Image.inflate(row[0]) for row in results]

    def public_networks(self) -> list[Network]:
        """list public networks this project can access.

        Make a cypher query to retrieve all public networks this project can access.
        """
        results, _ = self.cypher(
            f"""
                {self.query_prefix}
                WHERE q.type = "{ServiceType.NETWORK.value}"
                MATCH (q)-[:`APPLY_TO`]-(s)
                MATCH (s)-[:`AVAILABLE_NETWORK`]->(u:Network)
                WHERE u.is_shared = True
                RETURN u
            """
        )
        return [Network.inflate(row[0]) for row in results]
