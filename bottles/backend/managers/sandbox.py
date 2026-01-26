# steam.py
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


import glob
import os
import shlex
import subprocess
from typing import Optional


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
        self.envs = envs
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
        self.__uid = str(os.getuid())

    def __get_bwrap(self, cmd: str):
        _cmd = ["bwrap"]

        if self.envs:
            _cmd += [f"--setenv {k} {shlex.quote(v)}" for k, v in self.envs.items()]

        if self.share_host_ro:
            _cmd.append("--ro-bind / /")
            # Ensure standard system configs are available even if / is re-mounted
            for p in ["/etc/resolv.conf", "/etc/hosts", "/etc/passwd"]:
                if os.path.exists(p):
                    _cmd += ["--ro-bind", p, p]

        if self.chdir:
            _cmd.append(f"--chdir {shlex.quote(self.chdir)}")
            _cmd.append(f"--bind {shlex.quote(self.chdir)} {shlex.quote(self.chdir)}")

        if self.clear_env:
            _cmd.append("--clearenv")

        # Standard mounts for native apps
        _cmd += ["--dev", "/dev"]
        _cmd += ["--proc", "/proc"]
        _cmd += ["--tmpfs", "/tmp"]
        _cmd += ["--tmpfs", "/run"]

        if os.path.exists("/dev/shm"):
            _cmd += ["--bind", "/dev/shm", "/dev/shm"]

        if self.share_paths_ro:
            _cmd += [
                f"--ro-bind {shlex.quote(p)} {shlex.quote(p)}"
                for p in self.share_paths_ro
            ]

        if self.share_paths_rw:
            _cmd += [
                f"--bind {shlex.quote(p)} {shlex.quote(p)}" for p in self.share_paths_rw
            ]

        if self.share_sound:
            # PulseAudio/PipeWire socket discovery
            pulse_path = f"/run/user/{self.__uid}/pulse"
            if os.path.exists(pulse_path):
                _cmd.append(
                    f"--bind {shlex.quote(pulse_path)} {shlex.quote(pulse_path)}"
                )

            # Alsa fallback
            if os.path.exists("/dev/snd"):
                _cmd += ["--dev-bind", "/dev/snd", "/dev/snd"]

        if self.share_gpu:
            for device in glob.glob("/dev/dri/*"):
                _cmd += ["--dev-bind", shlex.quote(device), shlex.quote(device)]
            for device in glob.glob("/dev/nvidia*"):
                _cmd += ["--dev-bind", shlex.quote(device), shlex.quote(device)]

        if self.share_display:
            # X11/Wayland support
            x11_path = (
                f"/tmp/.X11-unix/X{os.environ.get('DISPLAY', ':0').split(':')[-1]}"
            )
            if os.path.exists(x11_path):
                _cmd += ["--bind", x11_path, x11_path]

            wayland_display = os.environ.get("WAYLAND_DISPLAY")
            if wayland_display:
                wayland_path = f"/run/user/{self.__uid}/{wayland_display}"
                if os.path.exists(wayland_path):
                    _cmd += ["--bind", wayland_path, wayland_path]

            for device in glob.glob("/dev/video*"):
                _cmd += ["--dev-bind", shlex.quote(device), shlex.quote(device)]

        _cmd.append("--share-net" if self.share_net else "--unshare-net")
        _cmd.append("--share-user" if self.share_user else "--unshare-user")
        _cmd.append(cmd)

        return _cmd

    def get_cmd(self, cmd: str):
        _cmd = self.__get_bwrap(cmd)
        return " ".join(_cmd)

    def run(self, cmd: str) -> subprocess.Popen[bytes]:
        return subprocess.Popen(
            self.get_cmd(cmd),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
