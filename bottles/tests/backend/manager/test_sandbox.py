"""Dedicated sandbox tests."""

from bottles.backend.managers.sandbox import SandboxManager
from bottles.backend.models.config import BottleConfig
from bottles.backend.utils.manager import ManagerUtils
from bottles.backend.wine.winecommand import WineCommand


def test_bwrap_input_devices_are_opt_in(monkeypatch):
    monkeypatch.delenv("FLATPAK_ID", raising=False)
    monkeypatch.setattr(
        "bottles.backend.managers.sandbox.os.path.isdir", lambda _: True
    )

    restricted = SandboxManager(share_input=False).get_cmd("true")
    shared = SandboxManager(share_input=True).get_cmd("true")

    assert "--tmpfs /dev/input" in restricted
    assert "--tmpfs /dev/input" not in shared
    assert "--dev-bind /dev/input /dev/input" in shared


def test_bwrap_usb_devices_are_opt_in(monkeypatch):
    monkeypatch.delenv("FLATPAK_ID", raising=False)
    monkeypatch.setattr(
        "bottles.backend.managers.sandbox.os.path.isdir", lambda _: True
    )

    restricted = SandboxManager(share_usb=False).get_cmd("true")
    shared = SandboxManager(share_usb=True).get_cmd("true")

    assert "--tmpfs /dev/bus/usb" in restricted
    assert "--tmpfs /dev/bus/usb" not in shared
    assert "--dev-bind /dev/bus/usb /dev/bus/usb" in shared


def test_bwrap_includes_dev_shm_and_pts(monkeypatch):
    monkeypatch.setattr(
        "bottles.backend.managers.sandbox.os.path.exists",
        lambda p: p in ("/dev/shm", "/dev/pts"),
    )

    command = SandboxManager().get_cmd("true")

    assert "--dev-bind-try /dev/shm /dev/shm" in command
    assert "--dev-bind-try /dev/pts /dev/pts" in command


def test_bwrap_forwards_desktop_environment(monkeypatch):
    monkeypatch.setenv("XDG_CURRENT_DESKTOP", "GNOME")
    monkeypatch.setenv("DESKTOP_SESSION", "gnome")
    monkeypatch.setenv("XDG_DATA_DIRS", "/usr/share")

    command = SandboxManager(share_display=True).get_cmd("true")

    assert "--setenv XDG_CURRENT_DESKTOP GNOME" in command
    assert "--setenv DESKTOP_SESSION gnome" in command
    assert "--setenv XDG_DATA_DIRS /usr/share" in command


def test_input_devices_are_opt_in():
    assert BottleConfig().Sandbox.share_input is False

    result = BottleConfig._fill_with({"Sandbox": {"share_input": True}})

    assert result.status is True
    assert result.data.Sandbox.share_input is True


def test_usb_devices_are_opt_in():
    assert BottleConfig().Sandbox.share_usb is False

    legacy = BottleConfig._fill_with({"Sandbox": {"share_input": True}})
    result = BottleConfig._fill_with({"Sandbox": {"share_usb": True}})

    assert legacy.status is True
    assert legacy.data.Sandbox.share_usb is False
    assert result.status is True
    assert result.data.Sandbox.share_usb is True


def test_wine_command_passes_input_permission(monkeypatch, tmp_path):
    command = object.__new__(WineCommand)
    command.config = BottleConfig(Name="Test", Path=str(tmp_path), Runner="sys-wine")
    command.config.Sandbox.share_input = True
    command.env = {}
    command.cwd = str(tmp_path)
    command.runner_runtime = None
    command.proton_script = None
    command.steam_runtime_root = None

    monkeypatch.setattr(ManagerUtils, "get_bottle_path", lambda _config: str(tmp_path))
    monkeypatch.setattr(ManagerUtils, "get_runner_path", lambda _runner: "sys-wine")

    sandbox = WineCommand._get_sandbox_manager(command)

    assert sandbox.share_input is True


def test_wine_command_passes_usb_permission(monkeypatch, tmp_path):
    command = object.__new__(WineCommand)
    command.config = BottleConfig(Name="Test", Path=str(tmp_path), Runner="sys-wine")
    command.config.Sandbox.share_usb = True
    command.env = {}
    command.cwd = str(tmp_path)
    command.runner_runtime = None
    command.proton_script = None
    command.steam_runtime_root = None

    monkeypatch.setattr(ManagerUtils, "get_bottle_path", lambda _config: str(tmp_path))
    monkeypatch.setattr(ManagerUtils, "get_runner_path", lambda _runner: "sys-wine")

    sandbox = WineCommand._get_sandbox_manager(command)

    assert sandbox.share_usb is True


def test_wine_command_coordinates_hidraw_sandbox_permissions(monkeypatch, tmp_path):
    command = object.__new__(WineCommand)
    command.config = BottleConfig(Name="Test", Path=str(tmp_path), Runner="sys-wine")
    command.config.Parameters.hidraw_devices = ["0x044F/0xB10A"]
    command.env = {}
    command.cwd = str(tmp_path)
    command.runner_runtime = None
    command.proton_script = None
    command.steam_runtime_root = None

    monkeypatch.setattr(ManagerUtils, "get_bottle_path", lambda _config: str(tmp_path))
    monkeypatch.setattr(ManagerUtils, "get_runner_path", lambda _runner: "sys-wine")

    sandbox = WineCommand._get_sandbox_manager(command)

    assert sandbox.share_input is True
    assert sandbox.share_usb is True
    assert sandbox.share_hidraw is True


def test_wine_command_rejects_invalid_hidraw_sandbox_permissions(monkeypatch, tmp_path):
    command = object.__new__(WineCommand)
    command.config = BottleConfig(Name="Test", Path=str(tmp_path), Runner="sys-wine")
    command.config.Parameters.hidraw_devices = ["1"]
    command.env = {}
    command.cwd = str(tmp_path)
    command.runner_runtime = None
    command.proton_script = None
    command.steam_runtime_root = None

    monkeypatch.setattr(ManagerUtils, "get_bottle_path", lambda _config: str(tmp_path))
    monkeypatch.setattr(ManagerUtils, "get_runner_path", lambda _runner: "sys-wine")

    sandbox = WineCommand._get_sandbox_manager(command)

    assert sandbox.share_input is False
    assert sandbox.share_usb is False
    assert sandbox.share_hidraw is False
