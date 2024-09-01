from typing import TypeVar

from neomodel import StructuredNode

from fed_reg.models import BaseNodeRead, BaseReadPrivate, BaseReadPublic

ModelType = TypeVar("ModelType", bound=StructuredNode)
SchemaReadPrivateType = TypeVar("SchemaReadPrivateType", bound=BaseReadPrivate)
SchemaReadPublicType = TypeVar("SchemaReadPublicType", bound=BaseReadPublic)
SchemaReadPrivateExtendedType = TypeVar(
    "SchemaReadPrivateExtendedType", BaseNodeRead, BaseReadPrivate, None
)
SchemaReadPublicExtendedType = TypeVar(
    "SchemaReadPublicExtendedType", BaseNodeRead, BaseReadPublic, None
)


def choose_out_schema(
    *,
    schema_read_public: type[SchemaReadPublicType],
    schema_read_private: type[SchemaReadPrivateType],
    schema_read_public_extended: type[SchemaReadPublicExtendedType],
    schema_read_private_extended: type[SchemaReadPrivateExtendedType],
    items: list[ModelType],
    auth: bool,
    with_conn: bool,
    short: bool,
) -> (
    list[SchemaReadPublicType]
    | list[SchemaReadPrivateType]
    | list[SchemaReadPublicExtendedType]
    | list[SchemaReadPrivateExtendedType]
):
    """Choose which read model use to return data to users.

    Based on authorization, and on the user request to retrieve linked items, choose
    one of the read schemas.

    Args:
    ----
        items (list[ModelType]): list of items to cast.
        auth (bool): Flag for authorization.
        with_conn (bool): Flag to retrieve linked items.
        short (bool): Only for authenticated users: show shrunk version (public).

    Returns:
    -------
        list[ReadPublicSchemaType] | list[ReadSchemaType] |
        list[ReadExtendedPublicSchemaType] | list[ReadExtendedSchemaType].
    """
    if auth:
        if short:
            if with_conn:
                return [schema_read_public_extended.from_orm(i) for i in items]
            return [schema_read_public.from_orm(i) for i in items]
        if with_conn:
            return [schema_read_private_extended.from_orm(i) for i in items]
        return [schema_read_private.from_orm(i) for i in items]
    if with_conn:
        return [schema_read_public_extended.from_orm(i) for i in items]
    return [schema_read_public.from_orm(i) for i in items]
