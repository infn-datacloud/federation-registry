"""Module with Create, Read, Update and Delete operations for a Location."""
from fed_reg.crud import CRUDInterface
from fed_reg.location.models import Location
from fed_reg.location.schemas import LocationCreate, LocationUpdate
from fed_reg.region.models import Region


class CRUDLocation(CRUDInterface[Location, LocationCreate, LocationUpdate]):
    """Location Create, Read, Update and Delete operations."""

    @property
    def model(self) -> type[Location]:
        return Location

    def create(self, *, obj_in: LocationCreate, region: Region) -> Location:
        """Create a new Location.

        At first check that a location with the given site name does not already exist.
        If it does not exist create it. Otherwise update its values without forcing
        default ones (some configuration may add new information to a location). In any
        case connect the location to the given region.
        """
        db_obj = self.get(site=obj_in.site)
        if not db_obj:
            db_obj = super().create(obj_in=obj_in)
        else:
            updated_data = self.update(db_obj=db_obj, obj_in=obj_in)
            if updated_data:
                db_obj = updated_data
        db_obj.regions.connect(region)
        return db_obj


location_mgr = CRUDLocation()
