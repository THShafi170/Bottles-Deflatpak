from bottles.backend.utils.vulkan import VulkanUtils


def test_vulkan_icd_dirs_includes_nixos_and_xdg(monkeypatch, tmp_path):
    custom_vulkan = tmp_path / "vulkan"
    custom_vulkan.mkdir()

    monkeypatch.setenv("XDG_DATA_DIRS", str(tmp_path))

    dirs = VulkanUtils.get_icd_dirs()

    assert "/run/opengl-driver/share/vulkan" in dirs
    assert "/run/current-system/sw/share/vulkan" in dirs
    assert str(custom_vulkan) in dirs
