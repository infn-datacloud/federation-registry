"""Neomodel model of the User Group owned by an Identity Provider."""
#

from neomodel import (
    One,
    RelationshipTo,
    StringProperty,
    StructuredNode,
    UniqueIdProperty,
    ZeroOrMore,
)

# from app.flavor.models import Flavor
# from app.image.models import Image
# from app.provider.models import Provider
# from app.service.models import Service


class UserGroup(StructuredNode):
    """User Group owned by an Identity Provider.

    A User Group has a name which could not be unique
    (different Identity Providers can have same user group names).
    A User Group can be involved into multiple SLAs.
    A UserGroup has access, through its SLAs and Projects to a set of
    images, flavors, networks and quotas.

    Attributes:
    ----------
        uid (int): User Group unique ID.
        description (str): Brief description.
        name (str): User Group name.
    """

    uid = UniqueIdProperty()
    description = StringProperty(default="")
    name = StringProperty(required=True)

    slas = RelationshipTo("fed_reg.sla.models.SLA", "AGREE", cardinality=ZeroOrMore)
    identity_provider = RelationshipTo(
        "fed_reg.identity_provider.models.IdentityProvider",
        "BELONG_TO",
        cardinality=One,
    )

    def pre_delete(self):
        """Remove related SLAs."""
        for item in self.slas:
            item.delete()

    # TODO Evaluate if they are useful depending on the dashboard communication
    # procedure.

    # query_prefix = """
    #     MATCH (g:UserGroup)
    #     WHERE (elementId(g)=$self)
    #     MATCH (g)-[:AGREE]-(s)-[:REFER_TO]->(p)
    #     """

    # def flavors(self) -> list[Flavor]:
    #     results, _ = self.cypher(
    #         f"""
    #             {self.query_prefix}
    #             MATCH (p)-[:CAN_USE_VM_FLAVOR]->(u)
    #             RETURN u
    #         """
    #     )
    #     return [Flavor.inflate(row[0]) for row in results]

    # def images(self) -> list[Image]:
    #     results, _ = self.cypher(
    #         f"""
    #             {self.query_prefix}
    #             MATCH (p)-[:CAN_USE_VM_IMAGE]->(u)
    #             RETURN u
    #         """
    #     )
    #     return [Image.inflate(row[0]) for row in results]

    # def providers(self) -> list[Provider]:
    #     results, _ = self.cypher(
    #         f"""
    #             {self.query_prefix}
    #             MATCH (p)<-[:BOOK_PROJECT_FOR_SLA]-(u)
    #             RETURN u
    #         """
    #     )
    #     return [Provider.inflate(row[0]) for row in results]

    # def services(self, **kwargs) -> list[Service]:
    #     if not kwargs:
    #         filters = ""
    #     else:
    #         filters = []
    #         for k in kwargs.keys():
    #             if k.startswith("service_"):
    #                 start_idx = len("service_")
    #                 attr = k[start_idx:]
    #                 filters.append(f"u.{attr} = ${k}")
    #             elif k.startswith("quota_"):
    #                 start_idx = len("quota_")
    #                 attr = k[start_idx:]
    #                 filters.append(f"q.{attr} = ${k}")
    #         filters = ", ".join(filters)
    #         filters = "WHERE " + filters

    #     results, _ = self.cypher(
    #         f"""
    #             {self.query_prefix}
    #             MATCH (p)-[:USE_SERVICE_WITH]->(q)-[:APPLY_TO]->(u)
    #             {filters}
    #             RETURN u
    #         """,
    #         kwargs,
    #     )
    #     return [Service.inflate(row[0]) for row in results]
