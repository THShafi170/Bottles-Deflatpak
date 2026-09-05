# ruff: noqa: E402
import os
from pathlib import Path
import urllib.error

from gi.repository import Gio

resource_path = Path(os.environ.get("BOTTLES_TEST_RESOURCE", "build/bottles.gresource"))
if not resource_path.is_file():
    resource_path = Path("/usr/share/bottles/bottles.gresource")
if resource_path.is_file():
    try:
        Gio.resources_register(Gio.Resource.load(str(resource_path)))
    except Exception:
        pass

from bottles.frontend.windows.installer import fetch_installer_icon


class Response:
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    @staticmethod
    def read():
        return b"icon"


def test_installer_icon_request_identifies_bottles(monkeypatch):
    captured = {}

    def urlopen(request, timeout):
        captured["request"] = request
        captured["timeout"] = timeout
        return Response()

    monkeypatch.setattr(
        "bottles.frontend.windows.installer.urllib.request.urlopen", urlopen
    )

    assert fetch_installer_icon("https://example.com/icon.png") == b"icon"
    assert captured["request"].get_header("User-agent") == "Bottles"
    assert captured["timeout"] == 10


def test_installer_icon_http_error_is_ignored(monkeypatch):
    def urlopen(_request, timeout):
        raise urllib.error.HTTPError(
            "https://example.com/icon.png", 403, "Forbidden", {}, None
        )

    monkeypatch.setattr(
        "bottles.frontend.windows.installer.urllib.request.urlopen", urlopen
    )

    assert fetch_installer_icon("https://example.com/icon.png") is None
