from uuid import uuid4

import pytest
from fedreg.identity_provider.models import IdentityProvider
from fedreg.project.models import Project
from fedreg.provider.models import Provider
from fedreg.provider.schemas_extended import ProviderCreateExtended
from fedreg.region.models import Region
from fedreg.sla.models import SLA
from fedreg.user_group.models import UserGroup
from pytest_cases import case, get_case_tags, parametrize, parametrize_with_cases

from fed_reg.provider.crud import provider_mgr
from tests.utils import (
    random_lower_string,
    random_provider_type,
    random_start_end_dates,
    random_url,
)


@pytest.fixture
def stand_alone_identity_provider_model() -> IdentityProvider:
    """Stand alone identity provider model."""
    idp = IdentityProvider(
        endpoint=random_url(), group_claim=random_lower_string()
    ).save()
    user_group = UserGroup(name=random_lower_string()).save()
    idp.user_groups.connect(user_group)
    return idp


@pytest.fixture
def provider_model() -> Provider:
    """Provider model."""
    provider = Provider(name=random_lower_string(), type=random_provider_type()).save()
    project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
    region = Region(name=random_lower_string()).save()
    idp = IdentityProvider(
        endpoint=random_url(), group_claim=random_lower_string()
    ).save()
    auth_method = {"protocol": random_lower_string(), "idp_name": random_lower_string()}
    provider.regions.connect(region)
    provider.projects.connect(project)
    provider.identity_providers.connect(idp, auth_method)
    return provider


@pytest.fixture
def sla_model(provider_model: Provider) -> SLA:
    """Stand alone identity provider model."""
    start_date, end_date = random_start_end_dates()
    user_group = UserGroup(name=random_lower_string()).save()
    sla = SLA(
        doc_uuid=str(uuid4()),
        start_date=start_date,
        end_date=end_date,
    ).save()
    idp = provider_model.identity_providers.single()
    project = provider_model.projects.single()
    idp.user_groups.connect(user_group)
    user_group.slas.connect(sla)
    sla.projects.connect(project)
    return sla


class CaseProvider:
    @case(tags="base")
    def case_provider_create(self) -> ProviderCreateExtended:
        return ProviderCreateExtended(
            name=random_lower_string(), type=random_provider_type()
        )

    @case(tags="regions")
    @parametrize(tot_reg=(1, 2))
    def case_provider_create_with_regions(self, tot_reg: int) -> ProviderCreateExtended:
        regions = []
        for _ in range(tot_reg):
            regions.append({"name": random_lower_string()})
        return ProviderCreateExtended(
            name=random_lower_string(), type=random_provider_type(), regions=regions
        )

    @case(tags="projects")
    @parametrize(tot_proj=(1, 2))
    def case_provider_create_with_projects(
        self, tot_proj: int
    ) -> ProviderCreateExtended:
        projects = []
        for _ in range(tot_proj):
            projects.append({"name": random_lower_string(), "uuid": uuid4()})
        return ProviderCreateExtended(
            name=random_lower_string(), type=random_provider_type(), projects=projects
        )

    @case(tags="idps")
    @parametrize(tot_idp=(1, 2))
    def case_provider_create_with_idps(self, tot_idp: int) -> ProviderCreateExtended:
        idps = []
        for _ in range(tot_idp):
            relationship = {
                "protocol": random_lower_string(),
                "idp_name": random_lower_string(),
            }
            idp = {
                "endpoint": random_url(),
                "group_claim": random_lower_string(),
                "relationship": relationship,
            }
            idps.append(idp)
        return ProviderCreateExtended(
            name=random_lower_string(),
            type=random_provider_type(),
            identity_providers=idps,
        )

    @case(tags="slas")
    @parametrize(tot_idps=(1, 2))
    @parametrize(tot_groups=(1, 2))
    def case_provider_create_with_idp_user_group_sla(
        self, tot_idps: int, tot_groups: int
    ) -> ProviderCreateExtended:
        """Each group of the identity providers linked to the provider has an SLA."""
        idps = []
        projects = []
        for _ in range(tot_idps):
            user_groups = []
            for _ in range(tot_groups):
                project = {"name": random_lower_string(), "uuid": uuid4()}
                start_date, end_date = random_start_end_dates()
                sla = {
                    "doc_uuid": uuid4(),
                    "start_date": start_date,
                    "end_date": end_date,
                    "project": project["uuid"],
                }
                user_group = {"name": random_lower_string(), "sla": sla}
                user_groups.append(user_group)
                projects.append(project)
            relationship = {
                "protocol": random_lower_string(),
                "idp_name": random_lower_string(),
            }
            idp = {
                "endpoint": random_url(),
                "group_claim": random_lower_string(),
                "relationship": relationship,
                "user_groups": user_groups,
            }
            idps.append(idp)
        return ProviderCreateExtended(
            name=random_lower_string(),
            type=random_provider_type(),
            identity_providers=idps,
            projects=projects,
        )

    @case(tags="existing-idp-diff-group")
    def case_provider_create_with_existing_idp(
        self, stand_alone_identity_provider_model: IdentityProvider
    ) -> ProviderCreateExtended:
        relationship = {
            "protocol": random_lower_string(),
            "idp_name": random_lower_string(),
        }
        idp = {
            "endpoint": stand_alone_identity_provider_model.endpoint,
            "group_claim": stand_alone_identity_provider_model.group_claim,
            "relationship": relationship,
        }
        return ProviderCreateExtended(
            name=random_lower_string(),
            type=random_provider_type(),
            identity_providers=[idp],
        )

    @case(tags="existing-idp-diff-group")
    def case_provider_create_with_existing_idps_add_group(
        self, stand_alone_identity_provider_model: IdentityProvider
    ) -> ProviderCreateExtended:
        project = {"name": random_lower_string(), "uuid": uuid4()}
        start_date, end_date = random_start_end_dates()
        sla = {
            "doc_uuid": uuid4(),
            "start_date": start_date,
            "end_date": end_date,
            "project": project["uuid"],
        }
        relationship = {
            "protocol": random_lower_string(),
            "idp_name": random_lower_string(),
        }
        idp = {
            "endpoint": stand_alone_identity_provider_model.endpoint,
            "group_claim": stand_alone_identity_provider_model.group_claim,
            "relationship": relationship,
            "user_groups": [{"name": random_lower_string(), "sla": sla}],
        }
        return ProviderCreateExtended(
            name=random_lower_string(),
            type=random_provider_type(),
            identity_providers=[idp],
            projects=[project],
        )

    @case(tags="existing-idp-same-group")
    def case_provider_create_with_existing_idps_same_group(
        self, stand_alone_identity_provider_model: IdentityProvider
    ) -> ProviderCreateExtended:
        project = {"name": random_lower_string(), "uuid": uuid4()}
        start_date, end_date = random_start_end_dates()
        sla = {
            "doc_uuid": uuid4(),
            "start_date": start_date,
            "end_date": end_date,
            "project": project["uuid"],
        }
        relationship = {
            "protocol": random_lower_string(),
            "idp_name": random_lower_string(),
        }
        idp = {
            "endpoint": stand_alone_identity_provider_model.endpoint,
            "group_claim": stand_alone_identity_provider_model.group_claim,
            "relationship": relationship,
            "user_groups": [
                {
                    "name": stand_alone_identity_provider_model.user_groups[0].name,
                    "sla": sla,
                }
            ],
        }
        return ProviderCreateExtended(
            name=random_lower_string(),
            type=random_provider_type(),
            identity_providers=[idp],
            projects=[project],
        )

    @case(tags="existing-idp-same-group")
    def case_provider_create_with_existing_idps_same_sla(
        self, sla_model: SLA
    ) -> ProviderCreateExtended:
        user_group_model = sla_model.user_group.single()
        idp_model = user_group_model.identity_provider.single()
        project = {"name": random_lower_string(), "uuid": uuid4()}
        sla = {
            "doc_uuid": sla_model.doc_uuid,
            "start_date": sla_model.start_date,
            "end_date": sla_model.end_date,
            "project": project["uuid"],
        }
        relationship = {
            "protocol": random_lower_string(),
            "idp_name": random_lower_string(),
        }
        idp = {
            "endpoint": idp_model.endpoint,
            "group_claim": idp_model.group_claim,
            "relationship": relationship,
            "user_groups": [{"name": user_group_model.name, "sla": sla}],
        }
        return ProviderCreateExtended(
            name=random_lower_string(),
            type=random_provider_type(),
            identity_providers=[idp],
            projects=[project],
        )


@parametrize_with_cases(
    "item",
    cases=CaseProvider,
    filter=lambda c: not any([i.startswith("existing-idp") for i in get_case_tags(c)]),
)
def test_create(item: ProviderCreateExtended) -> None:
    """Create a new istance"""
    db_obj = provider_mgr.create(obj_in=item)

    assert db_obj is not None
    assert isinstance(db_obj, Provider)
    assert len(db_obj.projects) == len(item.projects)
    assert len(db_obj.regions) == len(item.regions)
    assert len(db_obj.identity_providers) == len(item.identity_providers)
    for idp in db_obj.identity_providers:
        for user_group in idp.user_groups:
            for sla in user_group.slas:
                # By case construction, there is only one project per SLA
                project = sla.projects.single()
                assert db_obj.projects.get_or_none(uuid=project.uuid) is not None


@parametrize_with_cases("item", cases=CaseProvider, has_tag="existing-idp-diff-group")
def test_create_existing_idp_diff_user_group(item: ProviderCreateExtended) -> None:
    """Create a new istance and connect it to an existing IDP.

    Add a new user group if present and leave existing user groups untouched.
    """
    db_obj = provider_mgr.create(obj_in=item)

    assert db_obj is not None
    assert isinstance(db_obj, Provider)
    assert len(db_obj.identity_providers) == 1
    db_idp = db_obj.identity_providers.single()
    user_groups = item.identity_providers[0].user_groups

    if len(user_groups) == 0:
        assert len(db_idp.user_groups) == 1
    else:
        assert len(db_idp.user_groups) == 2

    for user_group in db_idp.user_groups:
        for sla in user_group.slas:
            # By case construction, there is only one project per SLA
            project = sla.projects.single()
            assert db_obj.projects.get_or_none(uuid=project.uuid) is not None


@parametrize_with_cases("item", cases=CaseProvider, has_tag="existing-idp-same-group")
def test_create_existing_idp_update_existing_user_group(
    item: ProviderCreateExtended,
) -> None:
    """Create a new istance and connect it to an existing IDP."""
    db_obj = provider_mgr.create(obj_in=item)

    assert db_obj is not None
    assert isinstance(db_obj, Provider)
    assert len(db_obj.identity_providers) == 1
    db_idp = db_obj.identity_providers.single()
    assert len(db_idp.user_groups) == 1
    for user_group in db_idp.user_groups:
        for sla in user_group.slas:
            if len(sla.projects) == 1:
                # By case construction, there is only one project per SLA
                project = sla.projects.single()
                assert db_obj.projects.get_or_none(uuid=project.uuid) is not None
            else:
                assert any(
                    [
                        db_obj.projects.get_or_none(uuid=project.uuid) is not None
                        for project in sla.projects
                    ]
                )


@parametrize_with_cases("item", cases=CaseProvider, has_tag="base")
def test_create_already_exists(
    item: ProviderCreateExtended, provider_model: Provider
) -> None:
    """A user_group with the given uuid already exists"""
    item.name = provider_model.name
    item.type = provider_model.type
    msg = f"Provider with name={item.name} and type={item.type} already exists."
    with pytest.raises(AssertionError, match=msg):
        provider_mgr.create(obj_in=item)


@parametrize_with_cases("item", cases=CaseProvider)
def test_update(item: ProviderCreateExtended, provider_model: Provider) -> None:
    """Completely update the user group attributes. Also override not set ones."""
    db_obj = provider_mgr.update(obj_in=item, db_obj=provider_model)

    assert db_obj is not None
    assert isinstance(db_obj, Provider)
    assert len(db_obj.projects) == len(item.projects)
    assert len(db_obj.regions) == len(item.regions)
    assert len(db_obj.identity_providers) == len(item.identity_providers)
    for idp in db_obj.identity_providers:
        for user_group in idp.user_groups:
            for sla in user_group.slas:
                # By case construction, there is only one project per SLA
                project = sla.projects.single()
                assert db_obj.projects.get_or_none(uuid=project.uuid) is not None


@parametrize_with_cases("item", cases=CaseProvider, has_tag="base")
def test_update_no_changes(
    item: ProviderCreateExtended, provider_model: Provider
) -> None:
    """The new item is equal to the existing one. No changes."""
    item.name = provider_model.name
    item.type = provider_model.type
    projects = []
    for project in provider_model.projects:
        projects.append({"name": project.name, "uuid": project.uuid})
    item.projects = projects
    regions = []
    for region in provider_model.regions:
        regions.append({"name": region.name})
    item.regions = regions
    idps = []
    for idp in provider_model.identity_providers:
        relationship = provider_model.identity_providers.relationship(idp)
        relationship = {
            "protocol": relationship.protocol,
            "idp_name": relationship.idp_name,
        }
        d = {
            "endpoint": idp.endpoint,
            "group_claim": idp.group_claim,
            "relationship": relationship,
        }
        idps.append(d)
    item.identity_providers = idps

    db_obj = provider_mgr.update(obj_in=item, db_obj=provider_model)

    assert db_obj is None


@parametrize_with_cases("item", cases=CaseProvider, has_tag="base")
def test_update_only_content(
    item: ProviderCreateExtended, provider_model: Provider
) -> None:
    """The new item is equal to the existing one. No changes."""
    projects = []
    for project in provider_model.projects:
        projects.append({"name": project.name, "uuid": project.uuid})
    item.projects = projects
    regions = []
    for region in provider_model.regions:
        regions.append({"name": region.name})
    item.regions = regions
    idps = []
    for idp in provider_model.identity_providers:
        relationship = provider_model.identity_providers.relationship(idp)
        relationship = {
            "protocol": relationship.protocol,
            "idp_name": relationship.idp_name,
        }
        d = {
            "endpoint": idp.endpoint,
            "group_claim": idp.group_claim,
            "relationship": relationship,
        }
        idps.append(d)
    item.identity_providers = idps

    db_obj = provider_mgr.update(obj_in=item, db_obj=provider_model)

    assert db_obj is not None
    assert isinstance(db_obj, Provider)
    assert len(db_obj.projects) == len(item.projects)
    assert len(db_obj.regions) == len(item.regions)
    assert len(db_obj.identity_providers) == len(item.identity_providers)
    for idp in db_obj.identity_providers:
        for user_group in idp.user_groups:
            for sla in user_group.slas:
                # By case construction, there is only one project per SLA
                project = sla.projects.single()
                assert db_obj.projects.get_or_none(uuid=project.uuid) is not None


@parametrize_with_cases("item", cases=CaseProvider, has_tag="base")
def test_update_only_projects(
    item: ProviderCreateExtended, provider_model: Provider
) -> None:
    """The new item is equal to the existing one. No changes."""
    item.name = provider_model.name
    item.type = provider_model.type
    regions = []
    for region in provider_model.regions:
        regions.append({"name": region.name})
    item.regions = regions
    idps = []
    for idp in provider_model.identity_providers:
        relationship = provider_model.identity_providers.relationship(idp)
        relationship = {
            "protocol": relationship.protocol,
            "idp_name": relationship.idp_name,
        }
        d = {
            "endpoint": idp.endpoint,
            "group_claim": idp.group_claim,
            "relationship": relationship,
        }
        idps.append(d)
    item.identity_providers = idps

    db_obj = provider_mgr.update(obj_in=item, db_obj=provider_model)

    assert db_obj is not None
    assert isinstance(db_obj, Provider)
    assert len(db_obj.projects) == len(item.projects)
    assert len(db_obj.regions) == len(item.regions)
    assert len(db_obj.identity_providers) == len(item.identity_providers)
    for idp in db_obj.identity_providers:
        for user_group in idp.user_groups:
            for sla in user_group.slas:
                # By case construction, there is only one project per SLA
                project = sla.projects.single()
                assert db_obj.projects.get_or_none(uuid=project.uuid) is not None


@parametrize_with_cases("item", cases=CaseProvider, has_tag="base")
def test_update_only_regions(
    item: ProviderCreateExtended, provider_model: Provider
) -> None:
    """The new item is equal to the existing one. No changes."""
    item.name = provider_model.name
    item.type = provider_model.type
    projects = []
    for project in provider_model.projects:
        projects.append({"name": project.name, "uuid": project.uuid})
    item.projects = projects
    idps = []
    for idp in provider_model.identity_providers:
        relationship = provider_model.identity_providers.relationship(idp)
        relationship = {
            "protocol": relationship.protocol,
            "idp_name": relationship.idp_name,
        }
        d = {
            "endpoint": idp.endpoint,
            "group_claim": idp.group_claim,
            "relationship": relationship,
        }
        idps.append(d)
    item.identity_providers = idps

    db_obj = provider_mgr.update(obj_in=item, db_obj=provider_model)

    assert db_obj is not None
    assert isinstance(db_obj, Provider)
    assert len(db_obj.projects) == len(item.projects)
    assert len(db_obj.regions) == len(item.regions)
    assert len(db_obj.identity_providers) == len(item.identity_providers)
    for idp in db_obj.identity_providers:
        for user_group in idp.user_groups:
            for sla in user_group.slas:
                # By case construction, there is only one project per SLA
                project = sla.projects.single()
                assert db_obj.projects.get_or_none(uuid=project.uuid) is not None


@parametrize_with_cases("item", cases=CaseProvider, has_tag="base")
def test_update_only_idps(
    item: ProviderCreateExtended, provider_model: Provider
) -> None:
    """The new item is equal to the existing one. No changes."""
    item.name = provider_model.name
    item.type = provider_model.type
    projects = []
    for project in provider_model.projects:
        projects.append({"name": project.name, "uuid": project.uuid})
    item.projects = projects
    regions = []
    for region in provider_model.regions:
        regions.append({"name": region.name})
    item.regions = regions

    db_obj = provider_mgr.update(obj_in=item, db_obj=provider_model)

    assert db_obj is not None
    assert isinstance(db_obj, Provider)
    assert len(db_obj.projects) == len(item.projects)
    assert len(db_obj.regions) == len(item.regions)
    assert len(db_obj.identity_providers) == len(item.identity_providers)
    for idp in db_obj.identity_providers:
        for user_group in idp.user_groups:
            for sla in user_group.slas:
                # By case construction, there is only one project per SLA
                project = sla.projects.single()
                assert db_obj.projects.get_or_none(uuid=project.uuid) is not None


@parametrize_with_cases("item", cases=CaseProvider, has_tag="base")
def test_update_only_idp_rel(
    item: ProviderCreateExtended, provider_model: Provider
) -> None:
    """The new item is equal to the existing one. No changes."""
    item.name = provider_model.name
    item.type = provider_model.type
    projects = []
    for project in provider_model.projects:
        projects.append({"name": project.name, "uuid": project.uuid})
    item.projects = projects
    regions = []
    for region in provider_model.regions:
        regions.append({"name": region.name})
    item.regions = regions
    idps = []
    for idp in provider_model.identity_providers:
        relationship = {
            "protocol": random_lower_string(),
            "idp_name": random_lower_string(),
        }
        d = {
            "endpoint": idp.endpoint,
            "group_claim": idp.group_claim,
            "relationship": relationship,
        }
        idps.append(d)
    item.identity_providers = idps

    db_obj = provider_mgr.update(obj_in=item, db_obj=provider_model)

    assert db_obj is not None
    assert isinstance(db_obj, Provider)
    assert len(db_obj.projects) == len(item.projects)
    assert len(db_obj.regions) == len(item.regions)
    assert len(db_obj.identity_providers) == len(item.identity_providers)
    for idp in db_obj.identity_providers:
        for user_group in idp.user_groups:
            for sla in user_group.slas:
                # By case construction, there is only one project per SLA
                project = sla.projects.single()
                assert db_obj.projects.get_or_none(uuid=project.uuid) is not None


# @parametrize_with_cases("item", cases=CaseProvider, has_tag="base")
# def test_update_only_content(
#     item: ProviderCreateExtended, provider_model: Provider
# ) -> None:
#     """The new item is equal to the existing one. No changes."""
#     item.name = provider_model.name
#     item.type = provider_model.type
#     projects = []
#     for project in provider_model.projects:
#         projects.append({"name": project.name, "uuid": project.uuid})
#     item.projects = projects
#     regions = []
#     for region in provider_model.regions:
#         regions.append({"name": region.name})
#     item.regions = regions
#     idps = []
#     for idp in provider_model.identity_providers:
#         relationship = provider_model.identity_providers.relationship(idp)
#         relationship = {
#             "protocol": relationship.protocol,
#             "idp_name": relationship.idp_name,
#         }
#         d = {
#             "endpoint": idp.endpoint,
#             "group_claim": idp.group_claim,
#             "relationship": relationship,
#         }
#         idps.append(d)
#     item.identity_providers = idps

#     db_obj = provider_mgr.update(obj_in=item, db_obj=provider_model)

#     assert db_obj is not None
#     assert isinstance(db_obj, Provider)
#     assert len(db_obj.projects) == len(item.projects)
#     assert len(db_obj.regions) == len(item.regions)
#     assert len(db_obj.identity_providers) == len(item.identity_providers)
#     for idp in db_obj.identity_providers:
#         for user_group in idp.user_groups:
#             for sla in user_group.slas:
#                 # By case construction, there is only one project per SLA
#                 project = sla.projects.single()
#                 assert db_obj.projects.get_or_none(uuid=project.uuid) is not None
