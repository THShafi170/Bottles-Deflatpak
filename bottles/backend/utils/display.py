import os
import subprocess
from functools import lru_cache


class DisplayUtils:
    @staticmethod
    @lru_cache
    def get_x_display():
        """Get the X display port."""
        if os.environ.get("DISPLAY"):
            return os.environ.get("DISPLAY")

        for i in range(3):
            _port = f":{i}"
            try:
                # Check if xdpyinfo reports a valid X.org display
                output = subprocess.check_output(
                    ["xdpyinfo", "-display", _port],
                    stderr=subprocess.DEVNULL,
                    text=True,
                ).lower()
                if "x.org" in output:
                    return _port
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass

        return False

    @staticmethod
    def check_nvidia_device():
        """Check if there is an nvidia device connected"""
        _query = "NVIDIA Corporation".lower()
        try:
            # Check lspci output for VGA controllers with NVIDIA vendor
            output = subprocess.check_output(["lspci"], text=True).lower()
            for line in output.splitlines():
                if "vga" in line and _query in line:
                    return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        return False

    @staticmethod
    def display_server_type():
        """Return the display server type"""
        return os.environ.get("XDG_SESSION_TYPE", "x11").lower()
