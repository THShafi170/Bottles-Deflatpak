# ruff: noqa: E402
# Tests for g_show_uri_handler — portal is preferred when Xdp is available,
# Gtk.show_uri is the fallback on a native install.

from typing import Any
from types import SimpleNamespace

from bottles.backend.models.result import Result


class PortalStub:
    directory_calls: list[Any] = []
    uri_calls: list[Any] = []

    def open_uri(self, *args):
        PortalStub.uri_calls.append(args)

    def open_directory(self, *args):
        PortalStub.directory_calls.append(args)


class XdpStub:
    Portal = PortalStub

    class OpenUriFlags:
        NONE = 0


class XdpGtk4Stub:
    @staticmethod
    def parent_new_gtk(_window):
        return object()


def _handler(uri, xdp, xdpgtk4, gtk_show_uri_fn, monkeypatch):
    """Helper: call g_show_uri_handler with the given stubs."""
    from bottles.frontend.windows import window as window_module

    monkeypatch.setattr(window_module, "Xdp", xdp)
    monkeypatch.setattr(window_module, "XdpGtk4", xdpgtk4)
    monkeypatch.setattr(window_module.Gtk, "show_uri", gtk_show_uri_fn)
    from bottles.frontend.windows.window import BottlesWindow

    BottlesWindow.g_show_uri_handler.__wrapped__(SimpleNamespace(), Result(data=uri))


def test_portal_used_for_file_uri_when_xdp_available(monkeypatch):
    uri = "file:///home/user/bottles"
    gtk_calls = []
    PortalStub.directory_calls = []
    PortalStub.uri_calls = []

    _handler(uri, XdpStub, XdpGtk4Stub, lambda *a: gtk_calls.append(a), monkeypatch)

    assert len(PortalStub.directory_calls) == 1
    assert PortalStub.directory_calls[0][1] == uri
    assert not PortalStub.uri_calls
    assert not gtk_calls


def test_portal_used_for_web_uri_when_xdp_available(monkeypatch):
    uri = "https://usebottles.com"
    gtk_calls = []
    PortalStub.directory_calls = []
    PortalStub.uri_calls = []

    _handler(uri, XdpStub, XdpGtk4Stub, lambda *a: gtk_calls.append(a), monkeypatch)

    assert len(PortalStub.uri_calls) == 1
    assert PortalStub.uri_calls[0][1] == uri
    assert not PortalStub.directory_calls
    assert not gtk_calls


def test_gtk_show_uri_used_as_fallback_when_xdp_unavailable(monkeypatch):
    uri = "https://usebottles.com"
    gtk_calls = []
    PortalStub.directory_calls = []
    PortalStub.uri_calls = []

    _handler(uri, None, None, lambda *a: gtk_calls.append(a), monkeypatch)

    assert len(gtk_calls) == 1
    assert gtk_calls[0][1] == uri
    assert not PortalStub.directory_calls
    assert not PortalStub.uri_calls
