"""Provider specific fixtures."""
from typing import Any, Dict, Optional, Tuple

from pytest_cases import fixture, parametrize

from app.provider.crud import CRUDProvider, provider_mng
from app.provider.models import Provider
from app.provider.schemas import ProviderBase, ProviderBasePublic
from app.provider.schemas_extended import ProviderCreateExtended
from tests.common.crud.validators import (
    CreateOperationValidation,
    DeleteOperationValidation,
    ReadOperationValidation,
)


@fixture
def provider_create_item_tuple(
    provider_create_valid_data, provider_create_operation_validator
) -> Tuple[
    CRUDProvider,
    CreateOperationValidation[
        ProviderBase, ProviderBasePublic, ProviderCreateExtended, Provider
    ],
    ProviderCreateExtended,
    Dict[str, Any],
]:
    """Fixture with the create class, validator and data to validate."""
    return (
        provider_mng,
        provider_create_operation_validator,
        ProviderCreateExtended(**provider_create_valid_data),
        {},
    )


# @fixture
# def provider_invalid_create_schema_tuple(
#     provider_create_invalid_data,
# ) -> Tuple[Type[ProviderCreateExtended], Dict[str, Any]]:
#     """Fixture with the create class and the invalid data to validate."""
#     return ProviderCreateExtended, provider_create_invalid_data


# @fixture
# def provider_valid_patch_schema_tuple(
#     provider_patch_validator, provider_patch_valid_data
# ) -> Tuple[
#     Type[ProviderUpdate],
#     PatchSchemaValidation[ProviderBase, ProviderBasePublic],
#     Dict[str, Any],
# ]:
#     """Fixture with the update class, validator and data to validate."""
#     return ProviderUpdate, provider_patch_validator, provider_patch_valid_data


# @fixture
# def provider_invalid_patch_schema_tuple(
#     provider_patch_invalid_data,
# ) -> Tuple[Type[ProviderUpdate], Dict[str, Any]]:
#     """Fixture with the update class and the invalid data to validate."""
#     return ProviderUpdate, provider_patch_invalid_data


@fixture
def provider_valid_read_item_tuple(
    provider_read_operation_validator, db_provider_simple
) -> Tuple[
    CRUDProvider,
    ReadOperationValidation[ProviderBase, ProviderBasePublic, Provider],
    Provider,
]:
    """Fixture with the read class, validator and the db item to read."""
    return provider_mng, provider_read_operation_validator, db_provider_simple


@fixture
def provider_valid_read_items_tuple(
    provider_read_operation_validator,
    db_provider_simple,
    db_provider_with_single_project,
) -> Tuple[
    CRUDProvider,
    ReadOperationValidation[ProviderBase, ProviderBasePublic, Provider],
    Provider,
]:
    """Fixture with the read class, validator and the db items to read."""
    return (
        provider_mng,
        provider_read_operation_validator,
        [db_provider_simple, db_provider_with_single_project],
    )


@fixture
def provider_delete_item_tuple(
    provider_delete_operation_validator, db_provider
) -> Tuple[
    CRUDProvider,
    DeleteOperationValidation[ProviderBase, ProviderBasePublic, Provider],
    Provider,
]:
    """Fixture with the delete class, validator and the db items to read."""
    return (
        provider_mng,
        provider_delete_operation_validator,
        db_provider,
    )


@fixture
@parametrize(attr=[*ProviderBase.__fields__.keys()])
def provider_attr(attr) -> Optional[str]:
    """Parametrized provider attribute."""
    return attr
