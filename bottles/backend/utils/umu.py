import shutil
import re


class UMUUtils:
    @staticmethod
    def get_umu_run_path() -> str | None:
        return shutil.which("umu-run")

    @staticmethod
    def find_umu_run() -> str | None:
        """
        Backward compatibility for find_umu_run.
        """
        return UMUUtils.get_umu_run_path()

    @staticmethod
    def is_umu_available() -> bool:
        return UMUUtils.get_umu_run_path() is not None

    @staticmethod
    def get_umu_id(program: dict) -> str:
        """
        Try to get a valid GAMEID for umu-launcher.
        """
        if "umu_id" in program:
            return program["umu_id"]

        args = program.get("arguments") or ""

        # Steam appid mapping
        if "steam://run/" in args or "steam://rungameid/" in args:
            match = re.search(r"steam://(?:run|rungameid)/(\d+)", args)
            if match:
                return f"umu-{match.group(1)}"

        # Epic AppName mapping
        if "com.epicgames.launcher://apps/" in args:
            match = re.search(r"apps/([^?]+)", args)
            if match:
                return match.group(1)

        # Ubisoft appid mapping
        if "uplay://launch/" in args:
            match = re.search(r"launch/(\d+)", args)
            if match:
                return match.group(1)

        # Fallback to AppID if present
        if "appid" in program:
            return f"umu-{program['appid']}"

        # Fallback to name/executable
        name = program.get("name", program.get("executable", "unknown"))
        return name.rsplit(".", 1)[0]

    @staticmethod
    def get_umu_store(program: dict) -> str:
        """
        Try to get the STORE for umu-launcher.
        """
        if "umu_store" in program:
            return program["umu_store"]

        args = program.get("arguments") or ""

        if "steam://" in args:
            return "steam"
        if "com.epicgames.launcher://" in args:
            return "egs"
        if "uplay://" in args:
            return "uplay"

        return "none"
