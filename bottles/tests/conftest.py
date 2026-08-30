import os
import sys


def _setup_test_env() -> None:
    this_dir = os.path.dirname(__file__)
    repo_root = os.path.abspath(os.path.join(this_dir, os.pardir, os.pardir))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    build_data = os.path.join(repo_root, "build", "data")
    data_dir = os.path.join(repo_root, "data")
    if os.path.isfile(os.path.join(build_data, "gschemas.compiled")):
        os.environ.setdefault("GSETTINGS_SCHEMA_DIR", build_data)
    elif os.path.isfile(os.path.join(data_dir, "gschemas.compiled")):
        os.environ.setdefault("GSETTINGS_SCHEMA_DIR", data_dir)
    os.environ.setdefault("GSETTINGS_BACKEND", "memory")


_setup_test_env()
