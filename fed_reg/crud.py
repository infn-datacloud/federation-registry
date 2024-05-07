"""Module with common Create, Read, Update and delete operations."""
from typing import Generic, List, Literal, Optional, Type, TypeVar, Union

from neomodel import StructuredNode

from fed_reg.models import BaseNodeCreate, BaseNodeRead

ModelType = TypeVar("ModelType", bound=StructuredNode)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseNodeCreate)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseNodeCreate)
ReadSchemaType = TypeVar("ReadSchemaType", bound=BaseNodeRead)
ReadPublicSchemaType = TypeVar("ReadPublicSchemaType", bound=BaseNodeRead)
ReadExtendedSchemaType = TypeVar("ReadExtendedSchemaType", BaseNodeRead, None)
ReadExtendedPublicSchemaType = TypeVar(
    "ReadExtendedPublicSchemaType", BaseNodeRead, None
)


class CRUDBase(
    Generic[
        ModelType,
        CreateSchemaType,
        UpdateSchemaType,
        ReadSchemaType,
        ReadPublicSchemaType,
        ReadExtendedSchemaType,
        ReadExtendedPublicSchemaType,
    ]
):
    """Class with common Create, Read, Update and delete operations."""

    def __init__(
        self,
        *,
        model: Type[ModelType],
        create_schema: Type[CreateSchemaType],
        read_schema: Type[ReadSchemaType],
        read_public_schema: Type[ReadPublicSchemaType],
        read_extended_schema: Type[ReadExtendedSchemaType],
        read_extended_public_schema: Type[ReadExtendedPublicSchemaType],
    ):
        """CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        Args:
        ----
            model (Type[ModelType]): A neomodel model used to read data from DB.
            create_schema (Type[CreateSchemaType]): A pydantic model to create add items
                to the DB.
            read_schema (Type[ReadSchemaType]): A pydantic model to return to users
                public and restricted data.
            read_public_schema (Type[ReadPublicSchemaType]): A pydantic model to return
                to users only public data.
            read_extended_schema (Type[ReadSchemaExtendedType]): A pydantic model
                to return to users public and restricted data.
            read_extended_public_schema (Type[ReadExtendedPublicSchemaType]): A pydantic
                model to return to users only public data.
        """
        self.model = model
        self.create_schema = create_schema
        self.read_schema = read_schema
        self.read_public_schema = read_public_schema
        self.read_extended_schema = read_extended_schema
        self.read_extended_public_schema = read_extended_public_schema

    def get(self, **kwargs) -> Optional[ModelType]:
        """Try to retrieve from DB an object with the given attributes.

        Args:
        ----
            **kwargs: Arbitrary keyword arguments used to filter the get operation.

        Returns:
        -------
            ModelType | None.
        """
        return self.model.nodes.get_or_none(**kwargs)

    def get_multi(
        self,
        *,
        skip: int = 0,
        limit: Optional[int] = None,
        sort: Optional[str] = None,
        **kwargs,
    ) -> List[ModelType]:
        """Try to retrieve from DB a list of objects with the given attributes.

        Args:
        ----
            skip (int): Number of items to skip from the first one received.
            limit (int | None): Maximum number of items to return.
            sort (int | None): Sorting rule.
            **kwargs: Arbitrary keyword arguments used to filter the get operation.

        Returns:
        -------
            List[ModelType].
        """
        sorting = []
        if sort:
            sorting = [sort, "uid"]
            if sort.startswith("-"):
                sorting = [sort, "-uid"]

        if kwargs:
            items = self.model.nodes.filter(**kwargs).order_by(*sorting).all()
        else:
            items = self.model.nodes.order_by(*sorting).all()

        return self.__apply_limit_and_skip(items=items, skip=skip, limit=limit)

    def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new node in the graph.

        Args:
        ----
            obj_in (CreateSchemaType): Input data to add to the DB.

        Returns:
        -------
            ModelType. The database object.
        """
        obj_in = self.create_schema.parse_obj(obj_in)
        obj_in_data = obj_in.dict(exclude_none=True)
        db_obj = self.model.create(obj_in_data)[0]
        return db_obj.save()

    def update(
        self,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
        force: bool = False,
    ) -> Optional[ModelType]:
        """Update and existing database object.

        Args:
        ----
            db_obj (ModelType): DB object to update.
            obj_in (UpdateSchemaType): Data to use to patch the DB object.
            force (bool): When this flag is True, if the new data contains unset values
                (alias default values), they will override the values written in the DB.
                By default unset values are ignored.

        Returns:
        -------
            ModelType | None. The updated DB object or None if there are no changes to
                apply.
        """
        obj_data = db_obj.__dict__
        update_data = obj_in.dict(exclude_unset=not force)

        if all(obj_data.get(k) == v for k, v in update_data.items()):
            return None

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        return db_obj.save()

    def remove(self, *, db_obj: ModelType) -> Literal[True]:
        """Delete the target instance from the DB.

        Args:
        ----
            db_obj (ModelType): DB object to delete.

        Returns:
        -------
            bool. True if the operations succeeded. Raises exception otherwise.
        """
        return db_obj.delete()

    def paginate(
        self, *, items: List[ModelType], page: int, size: Optional[int]
    ) -> List[ModelType]:
        """Divide the list in chunks.

        Args:
        ----
            items (list[ModelType]): List to split.
            page (int): Target chunk (start from 0).
            size (int | None): Chunk size.

        Returns:
        -------
            List[ModelType]. Chunk with index equal to page and length equal to, at
            most, size.
        """
        if size is None:
            return items
        start = page * size
        end = start + size
        return items[start:end]

    def choose_out_schema(
        self, *, items: List[ModelType], auth: bool, with_conn: bool, short: bool
    ) -> Union[
        List[ReadPublicSchemaType],
        List[ReadSchemaType],
        List[ReadExtendedPublicSchemaType],
        List[ReadExtendedSchemaType],
    ]:
        """Choose which read model use to return data to users.

        Based on authorization, and on the user request to retrieve linked items, choose
        one of the read schemas.

        Args:
        ----
            items (List[ModelType]): List of items to cast.
            auth (bool): Flag for authorization.
            with_conn (bool): Flag to retrieve linked items.
            short (bool): Only for authenticated users: show shrunk version (public).

        Returns:
        -------
            List[ReadPublicSchemaType] | List[ReadSchemaType] |
            List[ReadExtendedPublicSchemaType] | List[ReadExtendedSchemaType].
        """
        if auth:
            if short:
                if with_conn:
                    return [self.read_extended_public_schema.from_orm(i) for i in items]
                return [self.read_public_schema.from_orm(i) for i in items]
            if with_conn:
                return [self.read_extended_schema.from_orm(i) for i in items]
            return [self.read_schema.from_orm(i) for i in items]
        if with_conn:
            return [self.read_extended_public_schema.from_orm(i) for i in items]
        return [self.read_public_schema.from_orm(i) for i in items]

    def __apply_limit_and_skip(
        self, *, items: List[ModelType], skip: int = 0, limit: Optional[int] = None
    ) -> List[ModelType]:
        """Function to apply the limit and skip attributes on the list of values.

        Args:
        ----
            items (list[ModelType]): List to filter.
            skip (int): Number of items to skip from the first one received.
            limit (int | None): Maximum number of items to return.

        Returns:
        -------
            List[ModelType]. Restricted list
        """
        if limit is None:
            return items[skip:]
        start = skip
        end = skip + limit
        return items[start:end]
