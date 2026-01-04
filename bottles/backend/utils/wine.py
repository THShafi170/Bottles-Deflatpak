import os
from typing import Optional


class WineUtils:
    @staticmethod
    def get_user_dir(prefix_path: str):
        ignored = ["Public"]
        usersdir = os.path.join(prefix_path, "drive_c", "users")
        found = []

        for user_dir in os.listdir(usersdir):
            if user_dir in ignored:
                continue
            found.append(user_dir)

        if len(found) == 0:
            raise Exception("No user directories found.")

        return found[0]

    @staticmethod
    def find_system_wine() -> Optional[str]:
        """
        Find system wine binary in standard and common WineHQ paths.
        Returns the absolute path to the wine binary or None if not found.
        """
        import shutil

        # Common wine binary names
        binaries = ["wine", "wine64"]
        # Common WineHQ and system paths
        common_paths = [
            "/usr/bin",
            "/usr/local/bin",
            "/opt/wine-staging/bin",
            "/opt/wine-devel/bin",
            "/opt/wine-stable/bin",
        ]

        # 1. Check PATH using shutil.which
        for bin_name in binaries:
            path = shutil.which(bin_name)
            if path:
                return path

        # 2. Check common paths
        for path in common_paths:
            for bin_name in binaries:
                full_path = os.path.join(path, bin_name)
                if os.path.exists(full_path) and os.access(full_path, os.X_OK):
                    return full_path

        return None
