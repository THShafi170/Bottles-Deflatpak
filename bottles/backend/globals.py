# globals.py
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
import shutil
from pathlib import Path
from typing import Dict

from bottles.backend.utils import json, yaml


class Paths:
    xdg_data_home = os.environ.get(
        "XDG_DATA_HOME", os.path.join(Path.home(), ".local/share")
    )

    # Icon paths
    icons_user = f"{xdg_data_home}/icons"

    # Local paths
    base = f"{xdg_data_home}/bottles"

    # User applications path
    applications = f"{xdg_data_home}/applications/"

    temp = f"{base}/temp"
    runtimes = f"{base}/runtimes"
    winebridge = f"{base}/winebridge"
    runners = f"{base}/runners"
    bottles = f"{base}/bottles"
    steam = f"{base}/steam"
    d7vk = f"{base}/d7vk"
    dxvk = f"{base}/dxvk"
    vkd3d = f"{base}/vkd3d"
    nvapi = f"{base}/nvapi"
    latencyflex = f"{base}/latencyflex"
    templates = f"{base}/templates"
    library = f"{base}/library.yml"
    process_metrics = f"{base}/process_metrics.sqlite"

    @staticmethod
    def is_vkbasalt_available():
        vkbasalt_paths = [
            "/usr/lib/extensions/vulkan/vkBasalt/etc/vkBasalt",
            "/usr/local",
            "/usr/share/vkBasalt",
            "/run/current-system/sw/share/vkBasalt",
        ]
        for path in vkbasalt_paths:
            if os.path.exists(path):
                return True
        return False

    @staticmethod
    def get_lsfg_vk_version():
        layer_dirs = [
            path
            for path in os.environ.get("VK_ADD_LAYER_PATH", "").split(os.pathsep)
            if path
        ]
        layer_dirs += [
            "/usr/lib/extensions/vulkan/lsfgvk/share/vulkan/implicit_layer.d",
            f"{Paths.xdg_data_home}/vulkan/implicit_layer.d",
            "/usr/local/share/vulkan/implicit_layer.d",
            "/usr/share/vulkan/implicit_layer.d",
            "/etc/vulkan/implicit_layer.d",
        ]
        for version, manifest in (
            (2, "VkLayer_LSFGVK_frame_generation.json"),
            (1, "VkLayer_LS_frame_generation.json"),
        ):
            if any(
                os.path.isfile(os.path.join(layer_dir, manifest))
                for layer_dir in layer_dirs
            ):
                return version
        return 0


class TrdyPaths:
    # External managers paths
    wine = f"{Path.home()}/.wine"
    lutris = f"{Path.home()}/Games"
    playonlinux = f"{Path.home()}/.PlayOnLinux/wineprefix"
    bottlesv1 = f"{Path.home()}/.Bottles"


# check if bottles exists in xdg data path
os.makedirs(Paths.base, exist_ok=True)

try:
    os.getcwd()
except OSError:
    try:
        os.chdir(Paths.base)
    except OSError:
        pass

# Check if some tools are available — native host paths, no Flatpak extensions
gamemode_available = shutil.which("gamemoderun") or False
gamescope_available = shutil.which("gamescope") or False
hdr_wsi_available = any(
    os.path.exists(p)
    for p in [
        "/usr/lib/libVkLayer_hdr_wsi.so",
        "/usr/local/lib/libVkLayer_hdr_wsi.so",
        "/usr/share/vulkan/implicit_layer.d/VkLayer_hdr_wsi.json",
        "/etc/vulkan/implicit_layer.d/VkLayer_hdr_wsi.json",
        "/run/current-system/sw/share/vulkan/implicit_layer.d/VkLayer_hdr_wsi.json",
    ]
)
vkbasalt_available = Paths.is_vkbasalt_available()
lsfg_vk_version = Paths.get_lsfg_vk_version()
lsfg_vk_available = bool(lsfg_vk_version)
mangohud_available = shutil.which("mangohud") or False
obs_vkc_available = shutil.which("obs-vkcapture") or False
sandbox_available = shutil.which("bwrap") or False
vmtouch_available = shutil.which("vmtouch") or False
ntsync_available = os.path.exists("/dev/ntsync")

# encoding detection correction, following windows defaults
locale_encodings: Dict[str, str] = {"ja_JP": "cp932", "zh_CN": "gbk"}
