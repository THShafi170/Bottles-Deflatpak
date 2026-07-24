import os
from bottles.backend.managers.sandbox import SandboxManager


def test_sandbox_gpu_driver_paths(monkeypatch):
    """Test that share_gpu includes device nodes and Vulkan/EGL/DRI driver paths."""
    monkeypatch.setattr("bottles.backend.managers.sandbox.sandbox_available", True)

    manager = SandboxManager(share_gpu=True)
    cmd_list = manager.get_cmd_list("echo test")

    assert "--dev-bind" in cmd_list
    assert "/dev/dri" in cmd_list

    # Check driver paths ro-bind
    assert "--ro-bind" in cmd_list
    # Check that driver/ICD paths are properly searched
    assert any(
        p in cmd_list
        for p in [
            "/usr/share/vulkan",
            "/etc/vulkan",
            "/usr/share/glvnd",
            "/run/opengl-driver",
            "/usr/lib/dri",
            "/usr/lib64/dri",
            "/etc/static",
        ]
    )


def test_sandbox_share_user_home_binding(monkeypatch):
    """Test that share_user binds $HOME read-write and removes invalid --share-user."""
    monkeypatch.setattr("bottles.backend.managers.sandbox.sandbox_available", True)

    manager = SandboxManager(share_user=True)
    cmd_list = manager.get_cmd_list("echo test")

    home = os.path.expanduser("~")
    assert "--share-user" not in cmd_list
    assert "--bind" in cmd_list
    assert home in cmd_list
