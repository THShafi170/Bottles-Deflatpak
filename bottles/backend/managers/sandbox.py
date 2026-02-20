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
import subprocess
from typing import Optional, List


class SandboxManager:
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
        self.__uid = os.environ.get("UID", os.getuid())
        self.__xdg_runtime_dir = os.environ.get("XDG_RUNTIME_DIR")

    def __get_bwrap_args(self) -> List[str]:
        args = ["bwrap", "--unshare-all", "--die-with-parent"]

        # Environment variables
        if self.clear_env:
            args.append("--clearenv")
        for k, v in self.envs.items():
            args.extend(["--setenv", k, v])

        # Basic filesystem
        args.extend(["--proc", "/proc"])
        args.extend(["--dev", "/dev"])
        args.extend(["--tmpfs", "/tmp"])
        args.extend(["--dir", "/var"])
        args.extend(["--dir", "/run"])

        # Essential system paths
        for p in ["/usr", "/lib", "/lib64", "/bin", "/sbin"]:
            if os.path.exists(p):
                args.extend(["--ro-bind", p, p])

        # Essential config files
        for p in [
            "/etc/ld.so.cache",
            "/etc/ld.so.conf",
            "/etc/ld.so.conf.d",
            "/etc/alternatives",
            "/etc/fonts",
        ]:
            if os.path.exists(p):
                args.extend(["--ro-bind", p, p])

        # Host access
        if self.share_host_ro:
            args.extend(["--ro-bind-try", "/etc", "/etc"])
            # We don't bind-try / because it would override our unshare-all philosophy
            # but if the user explicitly wants share_host_ro, maybe they expect more?
            # For now, we stick to essential host bins/libs already added.

        # Working directory
        if self.chdir:
            args.extend(["--chdir", self.chdir])
            args.extend(["--bind", self.chdir, self.chdir])

        # Custom shared paths
        for p in self.share_paths_ro:
            if os.path.exists(p):
                args.extend(["--ro-bind", p, p])
        for p in self.share_paths_rw:
            if os.path.exists(p):
                args.extend(["--bind", p, p])

        # Networking
        if self.share_net:
            args.append("--share-net")
            # Need /etc/resolv.conf for DNS
            if os.path.exists("/etc/resolv.conf"):
                args.extend(["--ro-bind", "/etc/resolv.conf", "/etc/resolv.conf"])

        # User isolation
        if self.share_user:
            args.append("--share-user")

        # Display sharing
        if self.share_display:
            # X11
            x_display = os.environ.get("DISPLAY")
            if x_display:
                args.extend(["--setenv", "DISPLAY", x_display])
                display_num = x_display.split(":")[-1].split(".")[0]
                x_socket = f"/tmp/.X11-unix/X{display_num}"
                if os.path.exists(x_socket):
                    args.extend(["--bind", x_socket, x_socket])

                # Xauthority
                xauth = os.environ.get("XAUTHORITY") or os.path.expanduser(
                    "~/.Xauthority"
                )
                if os.path.exists(xauth):
                    args.extend(["--setenv", "XAUTHORITY", xauth])
                    args.extend(["--ro-bind", xauth, xauth])

            # Wayland
            wayland_display = os.environ.get("WAYLAND_DISPLAY")
            if wayland_display and self.__xdg_runtime_dir:
                args.extend(["--setenv", "WAYLAND_DISPLAY", wayland_display])
                wayland_socket = os.path.join(self.__xdg_runtime_dir, wayland_display)
                if os.path.exists(wayland_socket):
                    args.extend(["--bind", wayland_socket, wayland_socket])

        # Sound sharing
        if self.share_sound:
            if self.__xdg_runtime_dir:
                # PulseAudio
                pulse_socket = os.getenv("PULSE_SERVER")
                if pulse_socket and pulse_socket.startswith("unix:"):
                    pulse_path = pulse_socket[5:]
                    if os.path.exists(pulse_path):
                        args.extend(["--bind", pulse_path, pulse_path])
                else:
                    pulse_dir = os.path.join(self.__xdg_runtime_dir, "pulse")
                    if os.path.exists(pulse_dir):
                        args.extend(["--bind", pulse_dir, pulse_dir])

                # PipeWire
                pw_socket = os.path.join(self.__xdg_runtime_dir, "pipewire-0")
                if os.path.exists(pw_socket):
                    args.extend(["--bind", pw_socket, pw_socket])

        # GPU sharing
        if self.share_gpu:
            if os.path.exists("/dev/dri"):
                args.extend(["--dev-bind", "/dev/dri", "/dev/dri"])

            # NVIDIA support
            for i in range(16):
                dev = f"/dev/nvidia{i}"
                if os.path.exists(dev):
                    args.extend(["--dev-bind", dev, dev])
            for dev in [
                "/dev/nvidiactl",
                "/dev/nvidia-modeset",
                "/dev/nvidia-uvm",
                "/dev/nvidia-uvm-tools",
            ]:
                if os.path.exists(dev):
                    args.extend(["--dev-bind", dev, dev])

        return args

    def get_cmd_list(self, cmd: str) -> List[str]:
        args = self.__get_bwrap_args()
        # The command to run within bwrap
        # If cmd is a string, we might need to wrap it in a shell to handle arguments correctly
        # but Bottles usually passes the full command string.
        # To be safe and avoid shell injection, we'll try to split if it's a simple command.
        # However, Wine commands are often complex.
        # Let's use /bin/sh -c to run the command inside.
        args.extend(["/bin/sh", "-c", cmd])
        return args

    def get_cmd(self, cmd: str) -> str:
        return " ".join([shlex.quote(a) for a in self.get_cmd_list(cmd)])

    def run(self, cmd: str) -> subprocess.Popen[bytes]:
        return subprocess.Popen(
            self.get_cmd_list(cmd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
