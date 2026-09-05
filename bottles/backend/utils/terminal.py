# terminal.py
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

from bottles.backend.logger import Logger

logging = Logger()


class TerminalUtils:
    """
    This class is used to launch commands in the system terminal.
    It will loop all the "supported" terminals to find the one
    that is available, so it will be used to launch the command.
    """

    colors = {
        "default": "#00ffff #2b2d2e",
        "debug": "#ff9800 #2e2c2b",
        "easter": "#0bff00 #2b2e2c",
    }

    terminals = [
        # Desktop environments / Freedesktop standard
        ["xdg-terminal-exec", "sh -c %s"],
        ["konsole", "--noclose -e sh -c %s"],
        ["ptyxis", "-- sh -c %s"],
        ["gnome-terminal", "-- sh -c %s"],
        ["kgx", "-e sh -c %s"],
        ["cosmic-term", "-e sh -c %s"],
        ["xfce4-terminal", "--hold -x sh -c %s"],
        ["mate-terminal", "-x sh -c %s"],
        ["qterminal", "-e sh -c %s"],
        ["lxterminal", "-e sh -c %s"],
        # Distro alternative
        ["x-terminal-emulator", "-e sh -c %s"],
        # Third party
        ["ghostty", "-e sh -c %s"],
        ["alacritty", "--hold -e sh -c %s"],
        ["kitty", "--hold sh -c %s"],
        ["foot", "--hold sh -c %s"],
        ["wezterm", "start -- sh -c %s"],
        ["tilix", "-- sh -c %s"],
        ["st", "-e sh -c %s"],
        # Fallback
        ["xterm", "-hold -e sh -c %s"],
    ]

    def __init__(self):
        self.terminal = None

    def get_preferred_terminals(self) -> list[list[str]]:
        import shutil

        de = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
        session = os.environ.get("DESKTOP_SESSION", "").lower()

        # 1. Standard freedesktop terminal executor (if available)
        primary_names: list[str] = ["xdg-terminal-exec"]

        # 2. Desktop environment native terminals
        if "kde" in de or "plasma" in session:
            primary_names.extend(["konsole", "qterminal"])
        elif "gnome" in de or "gnome" in session:
            primary_names.extend(["ptyxis", "gnome-terminal", "kgx"])
        elif "cosmic" in de or "cosmic" in session:
            primary_names.append("cosmic-term")
        elif "xfce" in de or "xfce" in session:
            primary_names.append("xfce4-terminal")
        elif "mate" in de or "mate" in session:
            primary_names.append("mate-terminal")
        elif "lxqt" in de or "lxqt" in session:
            primary_names.append("qterminal")
        elif "cinnamon" in de or "cinnamon" in session:
            primary_names.append("gnome-terminal")

        # 3. System alternatives (Debian/Ubuntu/etc.)
        primary_names.append("x-terminal-emulator")

        # 4. User-defined TERMINAL environment variable (if set and binary exists)
        terminal_env = os.environ.get("TERMINAL", "").strip()
        env_term_entry: list[str] | None = None
        if terminal_env:
            parts = shlex.split(terminal_env)
            if parts and shutil.which(parts[0]):
                env_bin = parts[0]
                matched = next((t for t in self.terminals if t[0] == env_bin), None)
                if matched:
                    env_term_entry = matched
                else:
                    env_term_entry = [env_bin, "-e sh -c %s"]

        ordered: list[list[str]] = []

        # Add DE/standard primary candidates if known in self.terminals
        for name in primary_names:
            for term in self.terminals:
                if term[0] == name and term not in ordered:
                    ordered.append(term)

        # In standalone window managers (e.g. Sway, Hyprland, MangoWM, i3),
        # prioritize $TERMINAL if configured.
        is_full_de = any(
            env_name in de or env_name in session
            for env_name in [
                "kde",
                "plasma",
                "gnome",
                "cosmic",
                "xfce",
                "mate",
                "lxqt",
                "cinnamon",
            ]
        )
        if env_term_entry:
            if not is_full_de:
                if env_term_entry in ordered:
                    ordered.remove(env_term_entry)
                ordered.insert(0, env_term_entry)
            elif env_term_entry not in ordered:
                ordered.append(env_term_entry)

        # Append remaining supported terminals
        for term in self.terminals:
            if term not in ordered:
                ordered.append(term)

        return ordered

    def check_support(self) -> bool:
        import shutil

        for terminal in self.get_preferred_terminals():
            if shutil.which(terminal[0]):
                self.terminal = terminal
                return True

        return False

    @staticmethod
    def build_argv(
        terminal_entry: list[str] | tuple[str, ...], command: str
    ) -> list[str]:
        parts = list(terminal_entry)
        flat_parts: list[str] = []
        has_placeholder = False

        for p in parts:
            if "%s" in p:
                has_placeholder = True
                sub = shlex.split(p.replace("%s", "PLACEHOLDER"))
                for s in sub:
                    if "PLACEHOLDER" in s:
                        flat_parts.append("%s")
                    else:
                        flat_parts.append(s)
            else:
                flat_parts.extend(shlex.split(p))

        has_sh = "sh" in flat_parts and "-c" in flat_parts

        if has_placeholder:
            argv: list[str] = []
            for p in flat_parts:
                if p == "%s":
                    if not has_sh:
                        argv.extend(["sh", "-c", command])
                    else:
                        argv.append(command)
                else:
                    argv.append(p)
            return argv
        else:
            if not has_sh:
                return flat_parts + ["sh", "-c", command]
            return flat_parts + [command]

    def execute(self, command, env=None, colors="default", cwd=None):
        if env is None:
            env = os.environ.copy()
        else:
            env = env.copy()

        if not self.check_support():
            logging.warning("Terminal not supported.")
            return False

        if self.terminal is None:
            logging.warning("No terminal available.")
            return False

        command = str(command)
        argv = self.build_argv(self.terminal, command)

        logging.info(f"Command: {shlex.join(argv)}")

        try:
            proc = subprocess.Popen(
                argv,
                shell=False,
                env=env,
                cwd=cwd,
            )
            proc.communicate()
        except Exception as e:
            logging.warning(f"Failed to launch terminal command: {e}")
            return False

        return True

    def launch_snake(self):
        snake_path = os.path.dirname(os.path.realpath(__file__))
        snake_path = os.path.join(snake_path, "snake.py")
        self.execute(command=f"python {shlex.quote(snake_path)}", colors="easter")
