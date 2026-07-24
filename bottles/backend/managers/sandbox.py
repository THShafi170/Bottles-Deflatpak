# sandbox.py
#
# Copyright 2025 mirkobrombin <brombin94@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, in version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import os
import shlex
import signal
import subprocess
from typing import List, Optional

from bottles.backend.globals import sandbox_available


class SandboxManager:
    """
    Native bubblewrap sandbox manager for Bottles-Deflatpak.

    Uses bwrap with a deny-by-default policy and selectively shares only
    the resources (GPU, display, sound, network) requested by the bottle
    configuration. Falls back to unsandboxed execution when bwrap is not
    installed.

    Process tracking: running launcher PIDs are stored per WINEPREFIX so
    that terminate_prefix() can reliably kill the entire process group even
    when the Wine processes are grandchildren of the bwrap call.
    """

    # Per-WINEPREFIX list of running bwrap Popen handles.
    _running: dict[str, list[subprocess.Popen]] = {}

    def __init__(
        self,
        envs: Optional[dict] = None,
        chdir: Optional[str] = None,
        clear_env: bool = False,
        share_paths_ro: Optional[list] = None,
        share_paths_rw: Optional[list] = None,
        share_net: bool = False,
        share_user: bool = False,
        share_host_ro: bool = True,
        share_display: bool = True,
        share_sound: bool = True,
        share_gpu: bool = True,
    ):
        self.envs = envs or {}
        self.chdir = chdir
        self.clear_env = clear_env
        self.share_paths_ro = list(share_paths_ro or [])
        self.share_paths_rw = list(share_paths_rw or [])
        self.share_net = share_net
        self.share_user = share_user
        self.share_host_ro = share_host_ro
        self.share_display = share_display
        self.share_sound = share_sound
        self.share_gpu = share_gpu
        self.__uid = str(os.environ.get("UID", os.getuid()))
        self.__xdg_runtime_dir = os.environ.get("XDG_RUNTIME_DIR")

    def __get_bwrap_args(self) -> List[str]:
        args = ["bwrap", "--unshare-all", "--die-with-parent"]

        # Environment variables
        if self.clear_env:
            args.append("--clearenv")
        for k, v in self.envs.items():
            args.extend(["--setenv", k, str(v)])

        # Basic filesystem skeleton
        args.extend(["--proc", "/proc"])
        args.extend(["--dev", "/dev"])
        args.extend(["--tmpfs", "/tmp"])
        args.extend(["--dir", "/var"])
        args.extend(["--dir", "/run"])

        # Essential system paths (bind read-only where present)
        for p in [
            "/usr",
            "/lib",
            "/lib64",
            "/bin",
            "/sbin",
            # NixOS / immutable-rootfs distros
            "/nix/store",
            "/run/current-system",
        ]:
            if os.path.exists(p):
                args.extend(["--ro-bind", p, p])

        # Essential config & font files
        for p in [
            "/etc/ld.so.cache",
            "/etc/ld.so.conf",
            "/etc/ld.so.conf.d",
            "/etc/alternatives",
            "/etc/fonts",
            "/etc/localtime",
            "/etc/machine-id",
            "/usr/share/icons",
            "/usr/share/themes",
            "/usr/share/fontconfig",
        ]:
            if os.path.exists(p):
                args.extend(["--ro-bind", p, p])

        # Broader host read-only access (respects share_host_ro flag)
        if self.share_host_ro:
            args.extend(["--ro-bind-try", "/etc", "/etc"])

        # Working directory: expose and chdir into it
        if self.chdir:
            args.extend(["--chdir", self.chdir])
            args.extend(["--bind", self.chdir, self.chdir])

        # Caller-specified read-only paths
        for p in self.share_paths_ro:
            if p and os.path.exists(p):
                args.extend(["--ro-bind", p, p])

        # Caller-specified read-write paths
        for p in self.share_paths_rw:
            if p and os.path.exists(p):
                args.extend(["--bind", p, p])

        # D-Bus session socket (needed for display/sound forwarding)
        if (self.share_display or self.share_sound) and self.__xdg_runtime_dir:
            dbus_socket = os.path.join(self.__xdg_runtime_dir, "bus")
            if os.path.exists(dbus_socket):
                args.extend(["--bind", dbus_socket, dbus_socket])
                args.extend(
                    [
                        "--setenv",
                        "DBUS_SESSION_BUS_ADDRESS",
                        f"unix:path={dbus_socket}",
                    ]
                )

        # Networking
        if self.share_net:
            args.append("--share-net")
            if os.path.exists("/etc/resolv.conf"):
                args.extend(["--ro-bind", "/etc/resolv.conf", "/etc/resolv.conf"])

        # User namespace & Home directory sharing
        if self.share_user:
            home = os.path.expanduser("~")
            if os.path.exists(home):
                args.extend(["--bind", home, home])

        # Display sharing — X11 + Wayland
        if self.share_display:
            x_display = os.environ.get("DISPLAY")
            if x_display:
                args.extend(["--setenv", "DISPLAY", x_display])
                display_num = x_display.split(":")[-1].split(".")[0]
                x_socket = f"/tmp/.X11-unix/X{display_num}"
                if os.path.exists(x_socket):
                    args.extend(["--bind", x_socket, x_socket])
                xauth = os.environ.get("XAUTHORITY") or os.path.expanduser(
                    "~/.Xauthority"
                )
                if os.path.exists(xauth):
                    args.extend(["--setenv", "XAUTHORITY", xauth])
                    args.extend(["--ro-bind", xauth, xauth])

            wayland_display = os.environ.get("WAYLAND_DISPLAY")
            if wayland_display and self.__xdg_runtime_dir:
                args.extend(["--setenv", "WAYLAND_DISPLAY", wayland_display])
                wayland_socket = os.path.join(self.__xdg_runtime_dir, wayland_display)
                if os.path.exists(wayland_socket):
                    args.extend(["--bind", wayland_socket, wayland_socket])

        # Sound sharing — PulseAudio + PipeWire
        if self.share_sound and self.__xdg_runtime_dir:
            pulse_socket = os.getenv("PULSE_SERVER")
            if pulse_socket and pulse_socket.startswith("unix:"):
                pulse_path = pulse_socket[5:]
                if os.path.exists(pulse_path):
                    args.extend(["--bind", pulse_path, pulse_path])
            else:
                pulse_dir = os.path.join(self.__xdg_runtime_dir, "pulse")
                if os.path.exists(pulse_dir):
                    args.extend(["--bind", pulse_dir, pulse_dir])

            pw_socket = os.path.join(self.__xdg_runtime_dir, "pipewire-0")
            if os.path.exists(pw_socket):
                args.extend(["--bind", pw_socket, pw_socket])

        # GPU sharing — DRI + NVIDIA + Vulkan / EGL ICDs + NixOS OpenGL drivers
        if self.share_gpu:
            if os.path.exists("/dev/dri"):
                args.extend(["--dev-bind", "/dev/dri", "/dev/dri"])

            # Device nodes
            for i in range(16):
                dev = f"/dev/nvidia{i}"
                if os.path.exists(dev):
                    args.extend(["--dev-bind", dev, dev])
            for dev in [
                "/dev/nvidiactl",
                "/dev/nvidia-modeset",
                "/dev/nvidia-uvm",
                "/dev/nvidia-uvm-tools",
                "/dev/dma_heap",
                "/dev/ion",
            ]:
                if os.path.exists(dev):
                    args.extend(["--dev-bind", dev, dev])

            # Drivers & ICD manifests (Standard distros & NixOS)
            for p in [
                "/usr/share/vulkan",
                "/etc/vulkan",
                "/usr/share/glvnd",
                "/etc/glvnd",
                "/usr/lib/dri",
                "/usr/lib64/dri",
                "/usr/lib/x86_64-linux-gnu/dri",
                "/usr/lib/i386-linux-gnu/dri",
                "/run/opengl-driver",
                "/run/opengl-driver-32",
                "/etc/static",
            ]:
                if os.path.exists(p):
                    args.extend(["--ro-bind", p, p])

        return args

    def get_cmd_list(self, cmd: str) -> List[str]:
        """Return the full argv list for this sandboxed command."""
        if sandbox_available:
            args = self.__get_bwrap_args()
            args.extend(["/bin/sh", "-c", cmd])
            return args
        return ["/bin/sh", "-c", cmd]

    def get_cmd(self, cmd: str) -> str:
        """Return the full command as a shell-safe string."""
        return " ".join(shlex.quote(a) for a in self.get_cmd_list(cmd))

    def run(self, cmd: str) -> subprocess.Popen[bytes]:
        """Launch *cmd* inside the sandbox and return the Popen handle."""
        env = os.environ.copy()
        if not sandbox_available:
            # No bwrap: inject envs directly into the host environment copy.
            env.update(self.envs)

        proc = subprocess.Popen(
            self.get_cmd_list(cmd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
            env=env,
        )

        # Track by WINEPREFIX so terminate_prefix() can find this process.
        prefix = self.envs.get("WINEPREFIX")
        if prefix:
            self._running.setdefault(prefix, []).append(proc)

        return proc

    @classmethod
    def terminate_prefix(cls, prefix: str, sig: int = signal.SIGKILL) -> int:
        """
        Kill the process group of every sandbox launcher started for the
        given WINEPREFIX. Returns how many processes were signalled.
        Finished launchers are pruned from the tracking list.
        """
        killed = 0
        for proc in cls._running.get(prefix, []):
            if proc.poll() is not None:
                continue
            try:
                os.killpg(os.getpgid(proc.pid), sig)
                killed += 1
            except (ProcessLookupError, PermissionError, OSError):
                pass
        cls._running[prefix] = []
        return killed
