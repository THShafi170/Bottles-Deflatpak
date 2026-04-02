import re
import time
import subprocess
from typing import Optional

from bottles.backend.logger import Logger
from bottles.backend.wine.wineprogram import WineProgram
from bottles.backend.wine.wineserver import WineServer
from bottles.backend.wine.wineboot import WineBoot
from bottles.backend.utils.decorators import cache

logging = Logger()


class WineDbg(WineProgram):
    program = "Wine debug tool"
    command = "winedbg"
    colors = "debug"

    def __wineserver_status(self):
        return WineServer(self.config).is_alive()

    @cache(seconds=5)
    def get_processes(self):
        """Get all processes running on the wineprefix."""
        processes = []

        if not self.__wineserver_status():
            return processes

        res = self.launch(
            args='--command "info proc"', communicate=True, action_name="get_processes"
        )
        if not res.ready:
            return processes

        # Regex to match winedbg output:
        # pid (hex) | (D) flag | child marker \_ | threads (dec) | name (quoted or unquoted)
        # Examples:
        #  00000008 1      'C:\windows\system32\services.exe'
        #  00000009 1       \_ 'C:\windows\system32\winedevice.exe'
        #  00000020 (D) 1   'C:\windows\system32\services.exe'
        #  12345678 (D) \_ 2   name
        pattern = re.compile(
            r"^\s*"
            r"(?P<pid>[0-9a-fA-F]+)\s+"  # PID in hex
            r"(?:\(D\)\s+)?"  # Optional (D) flag
            r"(?P<child>\\_\s+)?"  # Optional child marker
            r"(?P<threads>\d+)\s+"  # Thread count
            r"(?P<name>.*)$"  # Executable name
        )

        lines = res.data.split("\n")
        last_pid = None

        for line in lines:
            line = line.strip()
            if not line or line.startswith("pid"):
                continue

            match = pattern.match(line)
            if not match:
                continue

            d = match.groupdict()
            w_pid = d["pid"]
            w_threads = d["threads"]
            w_name = d["name"].strip().strip("'").strip('"')
            is_child = bool(d["child"])

            # Determine parent PID
            w_parent = None
            if is_child:
                w_parent = last_pid
            else:
                last_pid = w_pid

            processes.append(
                {
                    "pid": w_pid,
                    "threads": w_threads,
                    "name": w_name,
                    "parent": w_parent,
                }
            )

        return processes

    def wait_for_process(self, name: str, timeout: float = 0.5):
        """Wait for a process to exit."""
        if not self.__wineserver_status():
            return True

        while True:
            processes = self.get_processes()
            if len(processes) == 0:
                break
            if name not in [p["name"] for p in processes]:
                break
            time.sleep(timeout)
        return True

    def kill_process(self, pid: Optional[str] = None, name: Optional[str] = None):
        """
        Kill a process by its PID or name.
        """
        wineboot = WineBoot(self.config)
        if not self.__wineserver_status():
            return

        if pid:
            args = "\n".join(
                ["<< END_OF_INPUTS", f"attach 0x{pid}", "kill", "quit", "END_OF_INPUTS"]
            )
            res = self.launch(args=args, communicate=True, action_name="kill_process")
            if res.has_data and "error 5" in res.data and name:
                subprocess.Popen(
                    f"kill $(pgrep {name[:15]})",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True,
                )
                return
            wineboot.kill()

        if name:
            processes = self.get_processes()
            for p in processes:
                if p["name"] == name:
                    self.kill_process(p["pid"], name)

    def is_process_alive(self, pid: Optional[str] = None, name: Optional[str] = None):
        """
        Check if a process is running on the wineprefix.
        """
        if not self.__wineserver_status():
            return False

        processes = self.get_processes()

        if pid:
            return pid in [p["pid"] for p in processes]
        if name:
            return name in [p["name"] for p in processes]
        return False
