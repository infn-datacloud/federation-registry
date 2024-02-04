"""Region specific fixtures."""
import copy
from typing import Any, Dict, List, Optional, Tuple

from pytest_cases import case, parametrize

from app.location.crud import location_mng
from app.provider.models import Provider
from app.provider.schemas_extended import RegionCreateExtended
from app.region.crud import CRUDRegion, region_mng
from app.region.models import Region
from app.region.schemas import RegionBase, RegionBasePublic, RegionUpdate
from app.service.crud import (
    block_storage_service_mng,
    compute_service_mng,
    identity_service_mng,
    network_service_mng,
)
from tests.common.crud.validators import (
    CreateOperationValidation,
    DeleteOperationValidation,
    PatchOperationValidation,
    ReadOperationValidation,
)
from tests.location.utils import random_location_required_attr
from tests.region.fixtures_patch_dict import (
    region_force_update_enriched_relationships_data,
    region_patch_not_equal_data,
)
from tests.region.utils import random_region_required_attr
from tests.services.block_storage_service.utils import (
    random_block_storage_service_required_attr,
)
from tests.services.compute_service.utils import random_compute_service_required_attr
from tests.services.identity_service.utils import random_identity_service_required_attr
from tests.services.network_service.utils import random_network_service_required_attr

region_get_attr = [*RegionBase.__fields__.keys(), "uid", None]
region_sort_attr = [*RegionBase.__fields__.keys(), "uid"]
region_patch_attr = [*RegionBase.__fields__.keys()]
region_patch_default_attr = [
    k for k, v in RegionBase.__fields__.items() if not v.required
]
region_patch_required_attr = [k for k, v in RegionBase.__fields__.items() if v.required]


@case(tags=["region", "not_existing"])
def case_region_not_existing_actors() -> CRUDRegion:
    """Return region manager."""
    return region_mng


@case(tags=["region", "create_item"])
def case_region_create_item_actors(
    region_create_valid_data: Dict[str, Any], db_provider_simple: Provider
) -> Tuple[
    CRUDRegion,
    CreateOperationValidation[
        RegionBase, RegionBasePublic, RegionCreateExtended, Region
    ],
    RegionCreateExtended,
    Dict[str, Any],
    List[str],
]:
    """Fixture with the create class, validator and data to validate."""
    validator = CreateOperationValidation[
        RegionBase, RegionBasePublic, RegionCreateExtended, Region
    ](base=RegionBase, base_public=RegionBasePublic, create=RegionCreateExtended)
    return (
        region_mng,
        validator,
        RegionCreateExtended(**region_create_valid_data),
        {"provider": db_provider_simple},
        ["provider"],
    )


@case(tags=["region", "read_single"])
@parametrize(attr=region_get_attr)
def case_region_read_item_actors(
    db_region_simple: Region, attr: str
) -> Tuple[
    CRUDRegion,
    ReadOperationValidation[RegionBase, RegionBasePublic, Region],
    Region,
    str,
]:
    """Fixture with the read class, validator and the db item to read."""
    validator = ReadOperationValidation[RegionBase, RegionBasePublic, Region](
        base=RegionBase, base_public=RegionBasePublic
    )
    return region_mng, validator, db_region_simple, attr


@case(tags=["region", "read_multi"])
@parametrize(attr=region_get_attr)
def case_region_read_items_actors(
    db_region_simple: Region, db_region_no_defaults: Region, attr: str
) -> Tuple[
    CRUDRegion,
    ReadOperationValidation[RegionBase, RegionBasePublic, Region],
    Region,
    str,
]:
    """Fixture with the read class, validator and the db items to read."""
    validator = ReadOperationValidation[RegionBase, RegionBasePublic, Region](
        base=RegionBase, base_public=RegionBasePublic
    )
    return (
        region_mng,
        validator,
        [db_region_no_defaults, db_region_simple],
        attr,
    )


@case(tags=["region", "sort"])
@parametrize(reverse=[True, False])
@parametrize(attr=region_sort_attr)
def case_region_read_items_sort(
    db_region_simple: Region,
    db_region_no_defaults: Region,
    reverse: bool,
    attr: str,
) -> Tuple[
    CRUDRegion,
    ReadOperationValidation[RegionBase, RegionBasePublic, Region],
    Region,
    str,
]:
    """Fixture with the read class, validator and the db item to read."""
    validator = ReadOperationValidation[RegionBase, RegionBasePublic, Region](
        base=RegionBase, base_public=RegionBasePublic
    )
    if reverse:
        attr = "-" + attr
    return (
        region_mng,
        validator,
        [db_region_no_defaults, db_region_simple],
        attr,
    )


@case(tags=["region", "skip"])
@parametrize(skip=[0, 1, 2])
def case_region_read_items_skip(
    db_region_simple: Region, db_region_no_defaults: Region, skip: int
) -> Tuple[
    CRUDRegion,
    ReadOperationValidation[RegionBase, RegionBasePublic, Region],
    Region,
    str,
]:
    """Fixture with the read class, validator and the db item to read."""
    validator = ReadOperationValidation[RegionBase, RegionBasePublic, Region](
        base=RegionBase, base_public=RegionBasePublic
    )
    return (
        region_mng,
        validator,
        [db_region_no_defaults, db_region_simple],
        skip,
    )


@case(tags=["region", "limit"])
@parametrize(limit=[None, 0, 1, 2, 3])
def case_region_read_items_limit(
    db_region_simple: Region,
    db_region_no_defaults: Region,
    limit: Optional[int],
) -> Tuple[
    CRUDRegion,
    ReadOperationValidation[RegionBase, RegionBasePublic, Region],
    Region,
    str,
]:
    """Fixture with the read class, validator and the db item to read."""
    validator = ReadOperationValidation[RegionBase, RegionBasePublic, Region](
        base=RegionBase, base_public=RegionBasePublic
    )
    return (
        region_mng,
        validator,
        [db_region_no_defaults, db_region_simple],
        limit,
    )


@case(tags=["region", "delete"])
def case_region_delete_item_actors(
    db_region: Region,
) -> Tuple[
    CRUDRegion,
    DeleteOperationValidation[RegionBase, RegionBasePublic, Region],
    Region,
]:
    """Fixture with the delete class, validator and the db items to read."""
    validator = DeleteOperationValidation[RegionBase, RegionBasePublic, Region](
        base=RegionBase,
        base_public=RegionBasePublic,
        managers={
            "location": location_mng,
            "block_storage_services": block_storage_service_mng,
            "compute_services": compute_service_mng,
            "identity_services": identity_service_mng,
            "network_services": network_service_mng,
        },
    )
    return region_mng, validator, db_region


@case(tags=["region", "patch"])
def case_region_patch_item_actors(
    db_region_simple: Region, region_patch_valid_data: Dict[str, Any]
) -> Tuple[
    CRUDRegion,
    PatchOperationValidation[RegionBase, RegionBasePublic, Region],
    Region,
    RegionUpdate,
]:
    """Fixture with the delete class, validator and the db items to read."""
    validator = PatchOperationValidation[RegionBase, RegionBasePublic, Region](
        base=RegionBase, base_public=RegionBasePublic
    )
    new_data = region_patch_not_equal_data(
        db_item=db_region_simple, new_data=region_patch_valid_data
    )
    return region_mng, validator, db_region_simple, RegionUpdate(**new_data)


@case(tags=["region", "patch"])
@parametrize(attr=region_patch_default_attr)
def case_region_patch_item_with_default_actors(
    db_region_no_defaults: Region, attr: str
) -> Tuple[CRUDRegion, Region, RegionUpdate]:
    """Fixture with the delete class, validator and the db items to read."""
    validator = PatchOperationValidation[RegionBase, RegionBasePublic, Region](
        base=RegionBase, base_public=RegionBasePublic
    )
    field_data = RegionUpdate.__fields__.get(attr)
    region_patch_valid_data = {attr: field_data.get_default()}
    return (
        region_mng,
        validator,
        db_region_no_defaults,
        RegionUpdate(**region_patch_valid_data),
    )


@case(tags=["region", "patch_required_with_none"])
@parametrize(attr=region_patch_required_attr)
def case_region_patch_item_required_with_none_actors(
    db_region_no_defaults: Region, attr: str
) -> Tuple[CRUDRegion, Region, RegionUpdate]:
    """Fixture with the delete class, validator and the db items to read."""
    field_data = RegionUpdate.__fields__.get(attr)
    region_patch_valid_data = {attr: field_data.get_default()}
    return (
        region_mng,
        db_region_no_defaults,
        RegionUpdate(**region_patch_valid_data),
    )


@case(tags=["region", "patch_no_changes"])
@parametrize(attr=region_patch_attr)
def case_region_patch_item_no_changes_actors(
    db_region_simple: Region, attr: str
) -> Tuple[CRUDRegion, Region, RegionUpdate]:
    """Fixture with the delete class, validator and the db items to read."""
    region_patch_valid_data = {attr: db_region_simple.__getattribute__(attr)}
    return (
        region_mng,
        db_region_simple,
        RegionUpdate(**region_patch_valid_data),
    )


@case(tags=["region", "force_update"])
def case_region_force_update_unchanged_rel_actors(
    region_create_with_rel: Dict[str, Any], db_provider_simple: Provider
) -> Tuple[
    CRUDRegion,
    PatchOperationValidation[RegionBase, RegionBasePublic, Region],
    Region,
    RegionUpdate,
]:
    """Fixture with the delete class, validator and the db items to read."""
    validator = PatchOperationValidation[RegionBase, RegionBasePublic, Region](
        base=RegionBase, base_public=RegionBasePublic
    )
    db_item = region_mng.create(
        obj_in=RegionCreateExtended(**region_create_with_rel),
        provider=db_provider_simple,
    )
    for k, v in random_region_required_attr().items():
        region_create_with_rel[k] = v
    return (
        region_mng,
        validator,
        db_item,
        RegionCreateExtended(**region_create_with_rel),
    )


@case(tags=["region", "force_update"])
@parametrize(start_empty=[True, False])
def case_region_force_update_add_rel_actors(
    start_empty: bool,
    region_create_with_rel: Dict[str, Any],
    db_provider_simple: Provider,
) -> Tuple[
    CRUDRegion,
    PatchOperationValidation[RegionBase, RegionBasePublic, Region],
    Region,
    RegionUpdate,
]:
    """Fixture with the delete class, validator and the db items to read."""
    validator = PatchOperationValidation[RegionBase, RegionBasePublic, Region](
        base=RegionBase, base_public=RegionBasePublic
    )
    if start_empty:
        starting_data = {
            **copy.deepcopy(region_create_with_rel),
            "location": None,
            "block_storage_services": [],
            "compute_services": [],
            "identity_services": [],
            "network_services": [],
        }
        new_data = region_create_with_rel
    else:
        new_data = region_force_update_enriched_relationships_data(
            region_create_with_rel
        )
        starting_data = region_create_with_rel
    db_item = region_mng.create(
        obj_in=RegionCreateExtended(**starting_data), provider=db_provider_simple
    )
    return region_mng, validator, db_item, RegionCreateExtended(**new_data)


@case(tags=["region", "force_update"])
@parametrize(end_empty=[True, False])
def case_region_force_update_remove_rel_actors(
    end_empty: bool,
    region_create_with_rel: Dict[str, Any],
    db_provider_simple: Provider,
) -> Tuple[
    CRUDRegion,
    PatchOperationValidation[RegionBase, RegionBasePublic, Region],
    Region,
    RegionUpdate,
]:
    """Fixture with the delete class, validator and the db items to read."""
    validator = PatchOperationValidation[RegionBase, RegionBasePublic, Region](
        base=RegionBase, base_public=RegionBasePublic
    )
    if end_empty:
        new_data = {
            **copy.deepcopy(region_create_with_rel),
            "location": None,
            "block_storage_services": [],
            "compute_services": [],
            "identity_services": [],
            "network_services": [],
        }
        starting_data = region_create_with_rel
    else:
        starting_data = region_force_update_enriched_relationships_data(
            region_create_with_rel
        )
        new_data = region_create_with_rel
    db_item = region_mng.create(
        obj_in=RegionCreateExtended(**starting_data), provider=db_provider_simple
    )
    return region_mng, validator, db_item, RegionCreateExtended(**new_data)


@case(tags=["region", "force_update"])
@parametrize(replace_all=[True, False])
def case_region_force_update_replace_rel_actors(
    replace_all: bool,
    region_create_with_rel: Dict[str, Any],
    db_provider_simple: Provider,
) -> Tuple[
    CRUDRegion,
    PatchOperationValidation[RegionBase, RegionBasePublic, Region],
    Region,
    RegionUpdate,
]:
    """Fixture with the delete class, validator and the db items to read."""
    validator = PatchOperationValidation[RegionBase, RegionBasePublic, Region](
        base=RegionBase, base_public=RegionBasePublic
    )
    if replace_all:
        starting_data = copy.deepcopy(region_create_with_rel)
    else:
        starting_data = region_force_update_enriched_relationships_data(
            region_create_with_rel
        )
    new_data = copy.deepcopy(region_create_with_rel)
    if new_data.get("location"):
        new_data["location"] = random_location_required_attr()
    if len(new_data.get("block_storage_services", [])) > 0:
        new_data["block_storage_services"] = [
            random_block_storage_service_required_attr()
        ]
    if len(new_data.get("compute_services", [])) > 0:
        new_data["compute_services"] = [random_compute_service_required_attr()]
    if len(new_data.get("identity_services", [])) > 0:
        new_data["identity_services"] = [random_identity_service_required_attr()]
    if len(new_data.get("network_services", [])) > 0:
        new_data["network_services"] = [random_network_service_required_attr()]
    db_item = region_mng.create(
        obj_in=RegionCreateExtended(**starting_data), provider=db_provider_simple
    )
    return region_mng, validator, db_item, RegionCreateExtended(**new_data)