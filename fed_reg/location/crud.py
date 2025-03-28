"""Module with Create, Read, Update and Delete operations for a Location."""

from fedreg.location.models import Location
from fedreg.location.schemas import (
    LocationCreate,
    LocationRead,
    LocationReadPublic,
    LocationUpdate,
)
from fedreg.location.schemas_extended import (
    LocationReadExtended,
    LocationReadExtendedPublic,
)
from fedreg.region.models import Region

from fed_reg.crud import CRUDBase


class CRUDLocation(
    CRUDBase[
        Location,
        LocationCreate,
        LocationUpdate,
        LocationRead,
        LocationReadPublic,
        LocationReadExtended,
        LocationReadExtendedPublic,
    ]
):
    """Location Create, Read, Update and Delete operations."""

    def create(
        self, *, obj_in: LocationCreate, region: Region | None = None
    ) -> Location:
        """Create a new Location.

        At first check that a location with the given site name does not already exist.
        If it does not exist create it. Otherwise update its values without forcing
        default ones (some configuration may add new information to a location). In any
        case connect the location to the given region. Eventually replace old location.

        A Location can exist without being connected to a region.
        """
        db_obj = self.get(site=obj_in.site)
        assert db_obj is None, f"A location with site name {obj_in.site} already exists"
        db_obj = super().create(obj_in=obj_in)
        if region:
            region_curr_location = region.location.single()
            if region_curr_location:
                region.location.reconnect(region_curr_location, db_obj)
            else:
                db_obj.regions.connect(region)
        return db_obj


location_mgr = CRUDLocation(
    model=Location,
    create_schema=LocationCreate,
    update_schema=LocationUpdate,
    read_schema=LocationRead,
    read_public_schema=LocationReadPublic,
    read_extended_schema=LocationReadExtended,
    read_extended_public_schema=LocationReadExtendedPublic,
)
