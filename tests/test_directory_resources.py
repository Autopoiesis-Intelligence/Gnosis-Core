from gnosis.evolution.directory_resources import (
    DirectoryResourceSnapshot,
    calculate_resource_delta,
)


def test_resource_delta_is_explicit_and_non_worsening() -> None:
    delta = calculate_resource_delta(
        DirectoryResourceSnapshot(file_count=10, byte_count=1000, estimated_work_units=20),
        DirectoryResourceSnapshot(file_count=9, byte_count=800, estimated_work_units=18),
    )
    assert delta.files == -1
    assert delta.bytes == -200
    assert delta.work_units == -2
    assert delta.non_worsening


def test_resource_delta_can_expose_regression() -> None:
    delta = calculate_resource_delta(
        DirectoryResourceSnapshot(file_count=10, byte_count=1000, estimated_work_units=20),
        DirectoryResourceSnapshot(file_count=9, byte_count=1200, estimated_work_units=25),
    )
    assert not delta.non_worsening
