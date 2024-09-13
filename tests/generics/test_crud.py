from typing import Literal

import pytest
from neomodel import IntegerProperty, StringProperty, StructuredNode
from neomodel.exceptions import MultipleNodesReturned
from pydantic import Field
from pytest_cases import parametrize_with_cases

from fed_reg.crud import CRUDInterface
from fed_reg.models import BaseNodeCreate
from tests.utils import random_lower_string, random_positive_int


class TestORMInt(StructuredNode):
    __test__ = False
    uid = StringProperty(default=random_lower_string())
    test_field = IntegerProperty()
    test_field_with_default = IntegerProperty()
    test_field_optional = IntegerProperty()


class TestModelCreateInt(BaseNodeCreate):
    __test__ = False
    test_field: int = Field(..., description="A test field for integers")
    test_field_with_default: int = Field(
        default=0, description="A test field for integers with default"
    )
    test_field_optional: int | None = Field(
        default=None, description="A test field for integers accepting None"
    )


class TestCRUDNoModelProperty(
    CRUDInterface[TestORMInt, TestModelCreateInt, TestModelCreateInt]
):
    __test__ = False


class TestCRUDNOSchemaCreateProperty(
    CRUDInterface[TestORMInt, TestModelCreateInt, TestModelCreateInt]
):
    __test__ = False

    @property
    def model(self) -> type[TestORMInt]:
        return TestORMInt


class TestCRUD(CRUDInterface[TestORMInt, TestModelCreateInt, TestModelCreateInt]):
    __test__ = False

    @property
    def model(self) -> type[TestORMInt]:
        return TestORMInt

    @property
    def schema_create(self) -> type[TestModelCreateInt]:
        return TestModelCreateInt


class CaseLen:
    def case_0(self) -> Literal[0]:
        return 0

    def case_1(self) -> Literal[1]:
        return 1

    def case_2(self) -> Literal[2]:
        return 2


@pytest.fixture
def schema_item() -> TestModelCreateInt:
    return TestModelCreateInt(test_field=random_positive_int())


@pytest.fixture
def model() -> TestORMInt:
    return TestORMInt(test_field=random_positive_int()).save()


@pytest.fixture
def another_model() -> TestORMInt:
    return TestORMInt(test_field=random_positive_int()).save()


def test_invalid_crud_classes():
    """Verify that classes with no model property defined raises TypeError."""
    with pytest.raises(TypeError):
        TestCRUDNoModelProperty()


def test_check_crud_properties():
    """Check model properties.

    The `model` property matches the neomodel class and `schema_create` is None if not
    defined otherwise it is the pydantic create class.
    """
    mgr = TestCRUDNOSchemaCreateProperty()
    assert mgr.model == TestORMInt
    assert mgr.schema_create is None

    mgr = TestCRUD()
    assert mgr.model == TestORMInt
    assert mgr.schema_create == TestModelCreateInt


def test_no_create(schema_item: TestModelCreateInt):
    """Test create.

    CRUD classes without the schema_create properties raises NotImplementedError when
    calling the create method.
    """
    mgr = TestCRUDNOSchemaCreateProperty()
    with pytest.raises(NotImplementedError):
        mgr.create(obj_in=schema_item)


def test_create(schema_item: TestModelCreateInt):
    """Test create.

    CRUD classes with the schema_create properties create a neomodel object with the
    provided attributes.
    """
    mgr = TestCRUD()
    db_obj = mgr.create(obj_in=schema_item)
    assert isinstance(db_obj, TestORMInt)
    assert db_obj.test_field == schema_item.test_field
    assert db_obj.test_field_with_default == schema_item.test_field_with_default
    assert db_obj.test_field_optional == schema_item.test_field_optional


def test_get(model: TestORMInt):
    """Retrieve the target model.

    When no attributes are provided it returns all the models in the DB. In this case
    just one.
    """
    mgr = TestCRUD()
    db_obj = mgr.get()
    assert isinstance(db_obj, TestORMInt)
    assert db_obj == model


def test_get_fail(model: TestORMInt, another_model: TestORMInt):
    """Retrieve the target model.

    When no attributes are provided it returns all the models in the DB. Since there are
    multiple instances, it raises a MultipleNodesReturned error.
    """

    mgr = TestCRUD()
    with pytest.raises(MultipleNodesReturned):
        mgr.get()


def test_get_with_attr(model: TestORMInt, another_model: TestORMInt):
    """Retrieve the target model.

    When attributes are provided it returns the model matching the given criteria.
    When there are multiple instances matching those criteria, it raises a
    MultipleNodesReturned error.
    If no models match given attributes return None.
    """

    mgr = TestCRUD()
    db_obj = mgr.get(test_field=model.test_field)
    assert db_obj == model

    db_obj = mgr.get(test_field__lt=0)  # Any item with test field < 0.
    assert db_obj is None

    with pytest.raises(MultipleNodesReturned):
        mgr.get(test_field__gt=0)  # Any item with test field > 0.


def test_get_multi_no_items():
    """Retrieve all models of this kind.

    When no attributes are provided it returns all the models in the DB.
    If there a no models it returns an empty list.
    """
    mgr = TestCRUD()
    db_items = mgr.get_multi()
    assert len(db_items) == 0


def test_get_multi_one_item(model: TestORMInt):
    """Retrieve all models of this kind."""
    mgr = TestCRUD()
    db_items = mgr.get_multi()
    assert len(db_items) == 1
    assert isinstance(db_items[0], TestORMInt)
    assert db_items[0] == model


def test_get_multi_two_items(model: TestORMInt, another_model: TestORMInt):
    """Retrieve all models of this kind."""
    models = [model, another_model]
    mgr = TestCRUD()
    db_items = mgr.get_multi()
    assert len(db_items) == 2
    for i, db_item in enumerate(db_items):
        assert isinstance(db_item, TestORMInt)
        assert db_item == models[i]


def test_get_multi_with_attr(model: TestORMInt, another_model: TestORMInt):
    """Retrieve all models of this kind, matching given attribute.

    When no models match given attributes returns empty list.
    """
    mgr = TestCRUD()
    db_items = mgr.get_multi(test_field=model.test_field)
    assert len(db_items) == 1
    assert db_items[0] == model

    db_items = mgr.get_multi(test_field__gt=0)
    assert len(db_items) == 2
    assert db_items[0] == model
    assert db_items[1] == another_model

    db_items = mgr.get_multi(test_field__lt=0)
    assert len(db_items) == 0


def test_get_multi_sorted(model: TestORMInt, another_model: TestORMInt):
    """Retrieve all models of this kind, sorted by specific field.

    Test both ascending and descending order.
    When the sorting attribute finds equal values, sort them by UID.
    """
    mgr = TestCRUD()
    db_items = mgr.get_multi(sort="test_field")
    assert len(db_items) == 2
    assert db_items[0].test_field <= db_items[1].test_field

    db_items = mgr.get_multi(sort="-test_field")
    assert len(db_items) == 2
    assert db_items[0].test_field >= db_items[1].test_field

    another_model.test_field = model.test_field
    db_items = mgr.get_multi(sort="test_field")
    assert len(db_items) == 2
    assert db_items[0].uid <= db_items[1].uid

    db_items = mgr.get_multi(sort="-test_field")
    assert len(db_items) == 2
    assert db_items[0].uid >= db_items[1].uid


@parametrize_with_cases("limit", cases=CaseLen)
def test_get_multi_with_limit(limit: int, model: TestORMInt, another_model: TestORMInt):
    """Limit params defines the max len of the CRUD returned list."""
    mgr = TestCRUD()
    db_items = mgr.get_multi(limit=limit)
    assert len(db_items) == limit
    if limit == 1:
        assert db_items[0] == model


@parametrize_with_cases("skip", cases=CaseLen)
def test_get_multi_with_skip(skip: int, model: TestORMInt, another_model: TestORMInt):
    """Skip params defines the items to skip from list returned by the DB query."""
    mgr = TestCRUD()
    db_items = mgr.get_multi(skip=skip)
    assert len(db_items) == 2 - skip
    if skip == 1:
        assert db_items[0] == another_model


@parametrize_with_cases("limit", cases=CaseLen)
@parametrize_with_cases("skip", cases=CaseLen)
def test_get_multi_with_skip_and_limit(
    limit: int, skip: int, model: TestORMInt, another_model: TestORMInt
):
    """Limit and skip can be combined.

    It skip the from the query returned list the first skip items, and limit the CRUD
    returned list up to limit. The total length is the min between the total size minus
    skip, and limit.
    """
    mgr = TestCRUD()
    db_items = mgr.get_multi(skip=skip, limit=limit)
    assert len(db_items) == min(2 - skip, limit)
    if len(db_items) == 1:
        if skip == 0:
            assert db_items[0] == model
        else:
            assert db_items[0] == another_model


def test_remove(model: TestORMInt):
    """Remove item from DB.

    Removing a second item an already deleted object raises a
    """
    mgr = TestCRUD()
    assert mgr.remove(db_obj=model)
    assert model.deleted

    with pytest.raises(ValueError, match="attempted on deleted node"):
        mgr.remove(db_obj=model)


def test_update(model: TestORMInt, schema_item: TestModelCreateInt):
    """Update existing model.

    When force is False (default value), the method updates only the set attributes.
    In this case it does not apply the new `test_field_with_default` and
    `test_field_optional` values since they are the default ones (not explicitly set).

    When None is explicitly set, it is applied.
    """
    model.test_field_with_default = random_positive_int()
    model.test_field_optional = random_positive_int()
    while model.test_field == schema_item.test_field:
        model.test_field = random_positive_int()

    mgr = TestCRUD()
    db_obj = mgr.update(db_obj=model, obj_in=schema_item)
    assert db_obj.test_field == schema_item.test_field
    assert db_obj.test_field_with_default != schema_item.test_field_with_default
    assert db_obj.test_field_optional != schema_item.test_field_optional

    # Explicit None value
    schema_item.test_field_optional = None
    db_obj = mgr.update(db_obj=model, obj_in=schema_item)
    assert db_obj.test_field == schema_item.test_field
    assert db_obj.test_field_with_default != schema_item.test_field_with_default
    assert db_obj.test_field_optional == schema_item.test_field_optional


def test_update_no_changes(model: TestORMInt, schema_item: TestModelCreateInt):
    """When there are no changes returns None."""
    schema_item.test_field = model.test_field

    mgr = TestCRUD()
    db_obj = mgr.update(db_obj=model, obj_in=schema_item)
    assert db_obj is None


def test_upda_with_force(model: TestORMInt, schema_item: TestModelCreateInt):
    """Update existing model.

    When force is True, the method applies the default values received.
    In this case it does not apply the new `test_field_with_default` and
    `test_field_optional` values since they are the default ones.
    """
    model.test_field_with_default = random_positive_int()
    model.test_field_optional = random_positive_int()
    while model.test_field == schema_item.test_field:
        model.test_field = random_positive_int()

    mgr = TestCRUD()
    db_obj = mgr.update(db_obj=model, obj_in=schema_item, force=True)
    assert db_obj.test_field == schema_item.test_field
    assert db_obj.test_field_with_default == schema_item.test_field_with_default
    assert db_obj.test_field_optional == schema_item.test_field_optional
