"""Module with common Create, Read, Update and delete operations."""

from typing import Generic, Literal, TypeVar

from fedreg.core import BaseNodeCreate
from fedreg.project.models import Project
from neomodel import StructuredNode

ModelType = TypeVar("ModelType", bound=StructuredNode)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseNodeCreate)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseNodeCreate)


class SkipLimit(Generic[ModelType]):
    """Class with a basic function to skip lists' initial values and trunk lists."""

    def _apply_limit_and_skip(
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


class CRUDBase(
    SkipLimit[ModelType],
    Generic[ModelType, CreateSchemaType, UpdateSchemaType],
):
    """Class with common Create, Read, Update and delete operations."""

    def __init__(
        self,
        *,
        model: type[ModelType],
        create_schema: type[CreateSchemaType],
        update_schema: type[UpdateSchemaType],
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
        super().__init__()
        self.__model = model
        self.__create_schema = create_schema
        self.__update_schema = update_schema

    @property
    def model(self):
        """Neomodel class."""
        return self.__model

    def get(self, **kwargs) -> ModelType | None:
        """Try to retrieve from DB an object with the given attributes.

        Args:
        ----
            **kwargs: Arbitrary keyword arguments used to filter the get operation.

        Returns:
        -------
            ModelType | None.
        """
        return self.__model.nodes.get_or_none(**kwargs)

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
            items = self.__model.nodes.filter(**kwargs).order_by(*sorting).all()
        else:
            items = self.__model.nodes.order_by(*sorting).all()

        return self._apply_limit_and_skip(items=items, skip=skip, limit=limit)

    def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new node in the graph.

        Args:
        ----
            obj_in (CreateSchemaType): Input data to add to the DB.

        Returns:
        -------
            ModelType. The database object.
        """
        obj_in = self.__create_schema.parse_obj(obj_in)
        obj_in_data = obj_in.dict(exclude_none=True)
        db_obj = self.__model.create(obj_in_data)[0]
        return db_obj.save()

    def patch(self, *, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType | None:
        """Patch an existing database object.

        Args:
        ----
            db_obj (ModelType): DB object to update.
            obj_in (UpdateSchemaType): Data to use to patch the DB object.

        Returns:
        -------
            ModelType | None. The updated DB object or None if there are no changes to
                apply.
        """
        if self._update(db_obj=db_obj, obj_in=obj_in):
            return db_obj.save()
        return None

    def update(
        self, *, db_obj: ModelType, obj_in: UpdateSchemaType
    ) -> ModelType | None:
        """Forcefully update an existing database object.

        If the new data contains unset values (alias default values), they will override
        the values written in the DB.

        Args:
        ----
            db_obj (ModelType): DB object to update.
            obj_in (UpdateSchemaType): Data to use to update the DB object.

        Returns:
        -------
            ModelType | None. The updated DB object or None if there are no changes to
                apply.
        """
        if self._update(db_obj=db_obj, obj_in=obj_in, force=True):
            return db_obj.save()
        return None

    def remove(self, *, db_obj: ModelType) -> Literal[True]:
        """Delete the target instance from the DB.

        Args:
        ----
            db_obj (ModelType): DB object to delete.

        Returns:
        -------
            bool. True if the operations succeeded. Raises exception otherwise.
        """
        return db_obj.deleted if hasattr(db_obj, "deleted") else db_obj.delete()

    def _update(
        self,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
        force: bool = False,
    ) -> bool:
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
        obj_in = self.__update_schema.parse_obj(obj_in)
        update_data = obj_in.dict(exclude_defaults=not force)

        if all(obj_data.get(k) == v for k, v in update_data.items()):
            return False

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        return True


CreateExtendedSchemaType = TypeVar("CreateExtendedSchemaType", bound=BaseNodeCreate)


class CRUDMultiProject(
    CRUDBase[ModelType, CreateSchemaType, UpdateSchemaType],
    Generic[ModelType, CreateSchemaType, CreateExtendedSchemaType, UpdateSchemaType],
):
    """Class with the function to merge new projects into current ones."""

    def update(
        self,
        *,
        db_obj: ModelType,
        obj_in: CreateExtendedSchemaType,
        provider_projects: list[Project],
    ) -> ModelType | None:
        """Update resource linked projects.

        Connect new projects not already connect, leave untouched already linked ones
        and delete old ones no more connected to the item.
        """
        assert len(provider_projects) > 0, "The provider's projects list is empty"

        edit = False
        db_items = {db_item.uuid: db_item for db_item in db_obj.projects}
        db_projects = {db_item.uuid: db_item for db_item in provider_projects}

        for proj in obj_in.projects:
            db_item = db_items.pop(proj, None)
            if not db_item:
                db_item = db_projects.get(proj)
                assert db_item is not None, (
                    f"Input project {proj} not in the provider "
                    f"projects: {[i.uuid for i in provider_projects]}"
                )
                db_obj.projects.connect(db_item)
                edit = True

        for db_item in db_items.values():
            db_obj.projects.disconnect(db_item)
            edit = True

        edit_content = self._update(db_obj=db_obj, obj_in=obj_in, force=True)

        return db_obj.save() if edit or edit_content else None

    def _connect_projects(
        self,
        *,
        db_obj: ModelType,
        input_uuids: list[str],
        provider_projects: list[Project],
    ) -> None:
        """Connect projects to the resource.

        If the intersection between the provider projects and the resource projects is
        empty rais an error.
        """
        filtered_projects = list(
            filter(lambda x: x.uuid in input_uuids, provider_projects)
        )
        assert len(filtered_projects) > 0, (
            f"None of the input projects {[i for i in input_uuids]} in the "
            f"provider projects: {[i.uuid for i in provider_projects]}"
        )
        for project in filtered_projects:
            db_obj.projects.connect(project)


PrivateModelType = TypeVar("PrivateModelType", bound=StructuredNode)
SharedModelType = TypeVar("SharedModelType", bound=StructuredNode)
PrivateCRUDType = TypeVar("PrivateModelType", bound=CRUDBase)
SharedCRUDType = TypeVar("SharedModelType", bound=CRUDBase)
PrivateCreateSchemaType = TypeVar("PrivateCreateSchemaType", bound=BaseNodeCreate)
SharedCreateSchemaType = TypeVar("SharedCreateSchemaType", bound=BaseNodeCreate)


class CRUDPrivateSharedDispatcher(
    SkipLimit[PrivateModelType | SharedModelType],
    Generic[
        PrivateModelType,
        SharedModelType,
        PrivateCRUDType,
        SharedCRUDType,
        PrivateCreateSchemaType,
        SharedCreateSchemaType,
        UpdateSchemaType,
    ],
):
    """Flavor (both shared and private) Create, Read, Update and Delete operations."""

    def __init__(
        self,
        *,
        private_mgr: PrivateCRUDType,
        shared_mgr: SharedCRUDType,
        shared_model: type[SharedModelType],
        shared_create_schema: type[SharedCreateSchemaType],
    ):
        self.__private_mgr = private_mgr
        self.__shared_mgr = shared_mgr
        self.__shared_model = shared_model
        self.__shared_create_schema = shared_create_schema

    def get(self, **kwargs) -> PrivateModelType | SharedModelType | None:
        """Get a single resource. Return None if the resource is not found."""
        item = self.__shared_mgr.get(**kwargs)
        if item:
            return item
        return self.__private_mgr.get(**kwargs)

    def get_multi(
        self, skip: int = 0, limit: int | None = None, sort: str | None = None, **kwargs
    ) -> list[PrivateModelType | SharedModelType]:
        """Get list of resources."""
        req_is_shared = kwargs.get("is_shared", None)

        if req_is_shared is None:
            shared_items = self.__shared_mgr.get_multi(**kwargs)
            private_items = self.__private_mgr.get_multi(**kwargs)

            items = [*shared_items, *private_items]
            if sort:
                if sort.startswith("-"):
                    sort = sort[1:]
                    reverse = True
                sorting = [sort, "uid"]
                items = sorted(
                    items,
                    key=lambda x: (x.__getattribute__(k) for k in sorting),
                    reverse=reverse,
                )

            return self._apply_limit_and_skip(items=items, skip=skip, limit=limit)

        if req_is_shared:
            return self.__shared_mgr.get_multi(
                skip=skip, limit=limit, sort=sort, **kwargs
            )
        return self.__private_mgr.get_multi(skip=skip, limit=limit, sort=sort, **kwargs)

    def create(
        self,
        *,
        obj_in: PrivateCreateSchemaType | SharedCreateSchemaType,
        provider_projects: list[Project] | None = None,
        **kwargs,
    ) -> PrivateModelType | SharedModelType:
        """Create a new resource."""
        if isinstance(obj_in, self.__shared_create_schema):
            return self.__shared_mgr.create(obj_in=obj_in, **kwargs)
        return self.__private_mgr.create(
            obj_in=obj_in, provider_projects=provider_projects, **kwargs
        )

    def update(
        self,
        *,
        db_obj: PrivateModelType | SharedModelType,
        obj_in: PrivateCreateSchemaType | SharedCreateSchemaType,
        provider_projects: list[Project] | None = None,
    ) -> PrivateModelType | SharedModelType | None:
        """Update and existing resource."""
        if isinstance(db_obj, self.__shared_model):
            return self.__shared_mgr.update(obj_in=obj_in, db_obj=db_obj)
        return self.__private_mgr.update(
            obj_in=obj_in, db_obj=db_obj, provider_projects=provider_projects
        )

    def patch(
        self, *, db_obj: PrivateModelType | SharedModelType, obj_in: UpdateSchemaType
    ) -> PrivateModelType | SharedModelType | None:
        """Patch an existing resource."""
        if isinstance(db_obj, self.__shared_model):
            return self.__shared_mgr.patch(obj_in=obj_in, db_obj=db_obj)
        return self.__private_mgr.patch(obj_in=obj_in, db_obj=db_obj)

    def remove(self, *, db_obj: PrivateModelType | SharedModelType) -> Literal[True]:
        """Remove an existing resource."""
        if isinstance(db_obj, self.__shared_model):
            return self.__shared_mgr.remove(db_obj=db_obj)
        return self.__private_mgr.remove(db_obj=db_obj)
