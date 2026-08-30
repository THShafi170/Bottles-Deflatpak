from bottles.backend.globals import Paths


def test_lsfg_vk_detects_layer_in_extension_path(monkeypatch):
    expected = (
        "/usr/lib/extensions/vulkan/lsfgvk/share/vulkan/implicit_layer.d/"
        "VkLayer_LS_frame_generation.json"
    )
    monkeypatch.setattr(
        "bottles.backend.globals.os.path.isfile",
        lambda path: path == expected,
    )

    assert Paths.get_lsfg_vk_version() == 1


def test_lsfg_vk_detects_version_two_user_install(monkeypatch):
    expected = (
        f"{Paths.xdg_data_home}/vulkan/implicit_layer.d/"
        "VkLayer_LSFGVK_frame_generation.json"
    )
    monkeypatch.setattr(
        "bottles.backend.globals.os.path.isfile",
        lambda path: path == expected,
    )

    assert Paths.get_lsfg_vk_version() == 2


def test_lsfg_vk_prefers_version_two(monkeypatch):
    manifests = {
        "/usr/share/vulkan/implicit_layer.d/VkLayer_LS_frame_generation.json",
        "/etc/vulkan/implicit_layer.d/VkLayer_LSFGVK_frame_generation.json",
    }
    monkeypatch.setattr(
        "bottles.backend.globals.os.path.isfile",
        lambda path: path in manifests,
    )

    assert Paths.get_lsfg_vk_version() == 2


def test_lsfg_vk_detects_custom_layer_path(monkeypatch, tmp_path):
    layer_dir = tmp_path / "layers"
    expected = layer_dir / "VkLayer_LS_frame_generation.json"
    monkeypatch.setenv("VK_ADD_LAYER_PATH", str(layer_dir))
    monkeypatch.setattr(
        "bottles.backend.globals.os.path.isfile",
        lambda path: path == str(expected),
    )

    assert Paths.get_lsfg_vk_version() == 1


def test_lsfg_vk_is_unavailable_without_layer_manifest(monkeypatch):
    monkeypatch.setattr(
        "bottles.backend.globals.os.path.isfile",
        lambda _path: False,
    )

    assert Paths.get_lsfg_vk_version() == 0
