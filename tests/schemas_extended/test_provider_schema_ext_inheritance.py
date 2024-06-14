from pytest_cases import filters as ft
from pytest_cases import parametrize_with_cases


@parametrize_with_cases(
    "child, parent", filter=ft.has_tag("read") | ft.has_tag("read_public")
)
def test_read(child, parent) -> None:
    assert issubclass(child, parent)
    assert child.__config__.orm_mode
