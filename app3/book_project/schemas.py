from ..models import (
    BaseProviderRelCreate,
    BaseProviderRelQuery,
    BaseProviderRelRead,
)


class BookProjectQuery(BaseProviderRelQuery):
    """BookProject Query Model class.

    Attributes:
        uuid (UUID4 | None): unique identifier of this item
            given by the provider.
        name (str | None): unique name of this item
            given by the provider.
    """


class BookProjectPatch(BaseProviderRelQuery):
    """BookProject Patch Model class.

    Class without id (which is populated by the database).
    Expected as input when performing a PATCH request.

    Attributes:
        uuid (UUID4 | None): unique identifier of this item
            given by the provider.
        name (str | None): unique name of this item
            given by the provider.
    """


class BookProjectCreate(BaseProviderRelCreate):
    """BookProject Create Model class.

    Class without id (which is populated by the database).
    Expected as input when performing a PUT or POST request.

    Attributes:
        uuid (UUID4): unique identifier of this item
            given by the provider.
        name (str): unique name of this item
            given by the provider.
    """


class BookProject(BookProjectCreate, BaseProviderRelRead):
    """BookProject class.

    Class retrieved from the database.
    Expected as output when performing a REST request.
    It contains all the non-sensible data written
    in the database.

    Attributes:
        uuid (UUID4): unique identifier of this item
            given by the provider.
        name (str): unique name of this item
            given by the provider.
    """