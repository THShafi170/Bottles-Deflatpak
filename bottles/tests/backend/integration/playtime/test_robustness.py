import pytest
from bottles.backend.managers.playtime import (
    _normalize_path_to_windows,
    _compute_program_id,
)


def test_normalize_path_none_empty():
    assert _normalize_path_to_windows("/path", None) == ""
    assert _normalize_path_to_windows("/path", "") == ""


def test_compute_program_id_robustness():
    # Should not crash with None/empty inputs
    pid1 = _compute_program_id(None, "/path", "/path/exe")
    assert isinstance(pid1, str)
    assert len(pid1) == 40

    pid2 = _compute_program_id("bottle", None, None)
    assert isinstance(pid2, str)
    assert len(pid2) == 40


def test_service_robustness(manager):
    from bottles.frontend.utils.playtime import PlaytimeService

    service = PlaytimeService(manager)

    # Should handle missing paths gracefully
    res = service.get_program_playtime("id", "/path", "name", None)
    assert res is None

    res = service.get_program_playtime("id", None, "name", "/exe")
    assert res is None
