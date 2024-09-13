from abc import ABC, abstractmethod
from typing import Generic, Literal, TypeVar

from neomodel import StructuredNode

from fed_reg.models import BaseNodeCreate

ModelType = TypeVar("ModelType", bound=StructuredNode)
SchemaCreateType = TypeVar("SchemaCreateType", bound=BaseNodeCreate)
SchemaUpdateType = TypeVar("SchemaUpdateType", bound=BaseNodeCreate)


class CRUDInterface(ABC, Generic[ModelType, SchemaCreateType, SchemaUpdateType]):
    """Create, Read, Update and Remove interface.

    This is an abstract class.

    The property 'model' is abstract and must be defined by the user.
    It returns the associated neomodel class.

    Functions 'create', 'get', 'get_multi', 'remove' and 'update' already have an
    implementation.
    """

    @property
    @abstractmethod
    def model(self) -> type[ModelType]:
        """Neomodel class."""
        ...

    @property
    def schema_create(self) -> type[SchemaCreateType] | None:
        """Pydantic Create schema.

        If not defined the create method is not available.
        """
        return None

    def __apply_limit_and_skip(
        self, *, items: list[ModelType], skip: int = 0, limit: int | None = None
    ) -> list[ModelType]:
        """Function to apply the limit and skip attributes on the list of values.

        Args:
        ----
            items (list[ModelType]): list to filter.
            skip (int): Number of items to skip from the first one received.
            limit (int | None): Maximum number of items to return.

        Returns:
        -------
            list[ModelType]. Restricted list
        """
        if limit is None:
            return items[skip:]
        start = skip
        end = skip + limit
        return items[start:end]

    def create(self, *, obj_in: SchemaCreateType) -> ModelType:
        """Create a new node in the graph.

        Args:
        ----
            obj_in (CreateSchemaType): Input data to add to the DB.

        Returns:
        -------
            ModelType. The database object.
        """
        if self.schema_create is None:
            raise NotImplementedError(
                "Since schema_create property has not been defined, "
                "create method can't be used for this class."
            )
        obj_in = self.schema_create.parse_obj(obj_in)
        obj_in_data = obj_in.dict(exclude_none=True)
        db_obj = self.model.create(obj_in_data)[0]
        return db_obj.save()

    def get(self, **kwargs) -> ModelType | None:
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
        limit: int | None = None,
        sort: str | None = None,
        **kwargs,
    ) -> list[ModelType]:
        """Try to retrieve from DB a list of objects with the given attributes.

        Args:
        ----
            skip (int): Number of items to skip from the first one received.
            limit (int | None): Maximum number of items to return.
            sort (int | None): Sorting rule.
            **kwargs: Arbitrary keyword arguments used to filter the get operation.

        Returns:
        -------
            list[ModelType].
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

    def update(
        self, *, db_obj: ModelType, obj_in: SchemaUpdateType, force: bool = False
    ) -> ModelType | None:
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
            ModelType | None. The updated DB object or None if there are no changes
                to apply.
        """
        obj_data = db_obj.__dict__
        update_data = obj_in.dict(exclude_unset=not force)

        if all(obj_data.get(k) == v for k, v in update_data.items()):
            return None

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        return db_obj.save()
