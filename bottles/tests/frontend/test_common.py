# ruff: noqa: E402

import pytest

from bottles.frontend.utils.common import format_runner_name, get_runner_icon_name


@pytest.mark.parametrize(
    ("runner", "expected"),
    [
        ("sys-wine-11.0", "sys-wine-11.0"),
        ("soda-11.0-3", "soda-11.0-3"),
        ("GE-Proton10-20", "GE-Proton10-20"),
    ],
)
def test_runner_name_is_unchanged(runner, expected):
    assert format_runner_name(runner) == expected


@pytest.mark.parametrize(
    ("runner", "expected"),
    [
        ("soda-11.0-4", "soda-runner"),
        ("Caffe-9.7", "caffe-runner"),
        ("vaniglia-8.0", "vaniglia-runner"),
        ("protosoda-11.1-2", "protosoda-runner"),
        ("GE-Proton10-20", None),
        ("sys-wine-11.0", None),
    ],
)
def test_runner_icon_name(runner, expected):
    assert get_runner_icon_name(runner) == expected
