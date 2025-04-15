from uuid import uuid4

import pytest
from fedreg.project.models import Project
from fedreg.provider.models import Provider

from tests.utils import random_lower_string, random_provider_type


@pytest.fixture
def stand_alone_project_model() -> Project:
    """Stand alone project model.

    Connected to a different provider.
    """
    provider = Provider(name=random_lower_string(), type=random_provider_type()).save()
    project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
    provider.projects.connect(project)
    return project
