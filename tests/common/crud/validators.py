"""Module to test Flavor schema creation."""
from typing import Dict, Generic, List, Type
from uuid import UUID

from pydantic.fields import SHAPE_LIST

from app.crud import CRUDBase
from tests.common.validators import (
    BasePublicType,
    BaseType,
    BaseValidation,
    CreateType,
    DbType,
)


class CreateOperationValidation(
    BaseValidation, Generic[BaseType, BasePublicType, CreateType, DbType]
):
    """Class with functions used to validate Create operations."""

    def __init__(
        self,
        *,
        base: Type[BaseType],
        base_public: Type[BasePublicType],
        create: Type[CreateType],
    ) -> None:
        """Define base, base public and create types.

        Args:
        ----
            base (type of BaseType): Schema class with public and private attributes.
            base_public (type of BasePublicType): Schema class with public attributes.
            create (type of CreateType): Schema class to create an instance.
        """
        super().__init__(base=base, base_public=base_public)
        self.create = create

    def validate_db_item_attrs(self, *, db_item: DbType, schema: CreateType) -> None:
        """Validate data attributes and relationships with the expected ones.

        Validate attributes and relationships.

        Args:
        ----
            db_item (DbType): Database instance with the created data. To be validated.
            schema (CreateType): Schema with the info to add to the database.
        """
        data = db_item.__dict__

        assert data.pop("uid")
        self.validate_attrs(data=data, schema=schema, public=False)

        attrs = self.create.__fields__.keys() - self.base.__fields__.keys()
        for attr in attrs:
            field = self.create.__fields__.get(attr)
            if field.shape == SHAPE_LIST:
                schema_list = schema.__getattribute__(attr)
                data_list = data.pop(attr, [])
                assert len(schema_list) == len(data_list)

                if isinstance(field.type_, str):
                    schema_list = sorted([x.uuid for x in schema_list])
                    data_list: List[UUID] = sorted(data_list)
                    for schema_str, data_str in zip(schema_list, data_list):
                        assert schema_str == data_str.hex
                else:
                    pass
            else:
                if issubclass(field.type_, str):
                    v: UUID = data.pop(attr, None)
                    v = v.hex if v else v
                    assert schema.__getattribute__(attr) == v
                else:
                    # We do not check this part since nested items checks are duplicates
                    # of other specific tests. We only pop the item if present.
                    data.pop(attr, None)

        assert data.pop("id")
        assert not data


class ReadOperationValidation(
    BaseValidation, Generic[BaseType, BasePublicType, DbType]
):
    """Class with functions used to validate Read operations."""

    def validate_retrieved_item(
        self, *, db_item: DbType, retrieved_item: DbType
    ) -> None:
        """Validate data attributes and relationships with the expected ones.

        Validate attributes and relationships.

        Args:
        ----
            db_item (DbType): Database instance.
            retrieved_item (DbType): Retrieved data. To be validated.
        """
        for k in self.base.__fields__.keys():
            assert db_item.__dict__.get(k) == retrieved_item.__dict__.get(k)


class DeleteOperationValidation(
    BaseValidation, Generic[BaseType, BasePublicType, DbType]
):
    """Class with functions used to validate Read operations."""

    def __init__(
        self,
        *,
        base: Type[BaseType],
        base_public: Type[BasePublicType],
        managers: Dict[str, CRUDBase],
    ) -> None:
        """Define base, base public and create types.

        Store the managers that will be used to check children deletion.

        Args:
        ----
            base (type of BaseType): Schema class with public and private attributes.
            base_public (type of BasePublicType): Schema class with public attributes.
            managers (dict): the key is the relationship name, the value is the manager.
        """
        super().__init__(base=base, base_public=base_public)
        self.managers = managers

    def store_rel_uids(self, *, db_item: DbType) -> None:
        """Store in this instance the uids of the relationships that will be deleted."""
        self.uids = {}
        for k in self.managers.keys():
            self.uids[k] = [i.uid for i in db_item.__getattribute__(k).all()]

    def validate_deleted_children(self, *, db_item: DbType) -> None:
        """Validate that target item and children entities have been deleted.

        Args:
        ----
            db_item (DbType): Deleted database instance.
            managers (DbType): Dict (key, manager).
        """
        assert db_item.deleted
        for k in self.managers:
            for uid in self.uids[k]:
                assert not self.managers[k].get(uid=uid)
