#!/usr/bin/env bash
# check.sh — run all quality checks for Bottles-Deflatpak
# Mirrors .pre-commit-config.yaml as closely as possible inside a venv.
# Nothing is installed system-wide.
#
# Usage:
#   ./check.sh              # check only (CI mode)
#   ./check.sh --fix        # auto-fix what ruff can fix
#   ./check.sh --all        # run mypy on ALL files (slow, shows upstream debt)
#
# Mypy scope (default):
#   Runs only on .py files changed relative to upstream/main, matching how
#   the pre-commit hook behaves in CI (it checks only staged/changed files).
#   --follow-imports=silent suppresses transitive errors in unchanged upstream
#   files that would otherwise flood the output.
#   Use --all to check everything.
#
# Differences from the GH workflow (pre-commit.yml):
#   - pygobject-stubs requires system GI typelib headers. On Fedora:
#       sudo dnf install gobject-introspection-devel python3-gobject-devel cairo-gobject-devel
#     When absent, mypy falls back to --ignore-missing-imports for gi.*.
#   - vkbasalt-cli is installed via a GitLab git URL in CI; skipped locally
#     (covered by the [mypy-vkbasalt] section in mypy.ini).

set -euo pipefail

FIX_MODE=0
ALL_FILES_MODE=0
for arg in "$@"; do
    case "$arg" in
        --fix) FIX_MODE=1 ;;
        --all) ALL_FILES_MODE=1 ;;
    esac
done

VENV_PATH="./venv"
PYTHON_BIN="$VENV_PATH/bin/python3"
PIP_BIN="$VENV_PATH/bin/pip"

# ---------------------------------------------------------------------------
# Tool versions — keep in sync with .pre-commit-config.yaml
# ---------------------------------------------------------------------------
RUFF_VERSION="0.15.15"
MYPY_VERSION="1.13.0"

# mypy additional_dependencies from .pre-commit-config.yaml
# (pygobject-stubs and vkbasalt-cli handled separately below)
MYPY_DEPS=(
    "types-PyYAML"
    "types-Markdown"
    "types-requests"
    "types-pycurl"
    "types-chardet"
    "types-freezegun"
    "pytest-stub"
    "pathvalidate"
    "requirements-parser"
    "icoextract"
    "patool"
)

# ---------------------------------------------------------------------------
# 1. Ensure venv exists
# ---------------------------------------------------------------------------
if [ ! -f "$PYTHON_BIN" ]; then
    echo "==> Creating virtual environment at $VENV_PATH ..."
    python3 -m venv "$VENV_PATH"
fi

# ---------------------------------------------------------------------------
# 2. Install / upgrade pinned tools if needed
# ---------------------------------------------------------------------------
_installed_version() {
    "$PYTHON_BIN" -c "
import importlib.metadata
try:
    print(importlib.metadata.version('$1'))
except importlib.metadata.PackageNotFoundError:
    print('')
" 2>/dev/null
}

echo ""
echo "==> Checking tool versions ..."

if [ "$(_installed_version ruff)" != "$RUFF_VERSION" ]; then
    echo "    Installing ruff==${RUFF_VERSION} ..."
    "$PIP_BIN" install --quiet "ruff==${RUFF_VERSION}"
fi

if [ "$(_installed_version mypy)" != "$MYPY_VERSION" ]; then
    echo "    Installing mypy==${MYPY_VERSION} ..."
    "$PIP_BIN" install --quiet "mypy==${MYPY_VERSION}"
fi

MISSING_DEPS=()
for dep in "${MYPY_DEPS[@]}"; do
    pkg="${dep%%[>=<!]*}"
    if [ -z "$(_installed_version "$pkg")" ]; then
        MISSING_DEPS+=("$dep")
    fi
done
if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo "    Installing mypy deps: ${MISSING_DEPS[*]} ..."
    "$PIP_BIN" install --quiet "${MISSING_DEPS[@]}"
fi

# pygobject-stubs: requires system GI headers.
# On Fedora: sudo dnf install gobject-introspection-devel python3-gobject-devel cairo-gobject-devel
HAS_PYGOBJECT_STUBS=0
if [ -n "$(_installed_version pygobject-stubs)" ]; then
    HAS_PYGOBJECT_STUBS=1
else
    echo "    Attempting pygobject-stubs (requires system GI headers) ..."
    if "$PIP_BIN" install --quiet "pygobject-stubs" 2>/dev/null; then
        HAS_PYGOBJECT_STUBS=1
        echo "    pygobject-stubs installed."
    else
        echo "    pygobject-stubs unavailable -- mypy will use --ignore-missing-imports for gi.*"
    fi
fi

# ---------------------------------------------------------------------------
# 3. Resolve mypy target files
#    Default: .py files changed vs upstream/main merge-base.
#    --all: the full tree.
# ---------------------------------------------------------------------------
MYPY_TARGETS=()

if [ "$ALL_FILES_MODE" -eq 1 ]; then
    MYPY_TARGETS=(.)
else
    MERGE_BASE=""
    if git rev-parse upstream/main &>/dev/null; then
        MERGE_BASE=$(git merge-base HEAD upstream/main 2>/dev/null || true)
    fi

    if [ -n "$MERGE_BASE" ]; then
        while IFS= read -r f; do
            [ -f "$f" ] && MYPY_TARGETS+=("$f")
        done < <(git diff --name-only "$MERGE_BASE" HEAD -- '*.py' 2>/dev/null || true)
    else
        while IFS= read -r f; do
            [ -f "$f" ] && MYPY_TARGETS+=("$f")
        done < <(git diff --name-only HEAD^ HEAD -- '*.py' 2>/dev/null || true)
    fi

    if [ ${#MYPY_TARGETS[@]} -eq 0 ]; then
        echo ""
        echo "    No changed Python files detected for mypy -- skipping."
    fi
fi

# ---------------------------------------------------------------------------
# 4. Track overall exit code — run all checks even if one fails
# ---------------------------------------------------------------------------
OVERALL=0

run_check() {
    local label="$1"; shift
    echo ""
    echo "--- $label ---"
    if "$@"; then
        echo "OK  $label passed"
    else
        echo "FAIL  $label FAILED"
        OVERALL=1
    fi
}

# ---------------------------------------------------------------------------
# 5. Ruff lint
# ---------------------------------------------------------------------------
if [ "$FIX_MODE" -eq 1 ]; then
    run_check "Ruff lint" "$VENV_PATH/bin/ruff" check --fix .
else
    run_check "Ruff lint" "$VENV_PATH/bin/ruff" check .
fi

# ---------------------------------------------------------------------------
# 6. Ruff format
# ---------------------------------------------------------------------------
if [ "$FIX_MODE" -eq 1 ]; then
    run_check "Ruff format" "$VENV_PATH/bin/ruff" format .
else
    run_check "Ruff format" "$VENV_PATH/bin/ruff" format --check .
fi

# ---------------------------------------------------------------------------
# 7. mypy
#    --follow-imports=silent: only report errors in the explicitly listed
#    files, suppress transitive errors in unchanged upstream files.
#    --ignore-missing-imports: fallback when pygobject-stubs are unavailable.
# ---------------------------------------------------------------------------
if [ ${#MYPY_TARGETS[@]} -gt 0 ]; then
    MYPY_ARGS=(--pretty)

    if [ "$HAS_PYGOBJECT_STUBS" -eq 0 ]; then
        MYPY_ARGS+=(--ignore-missing-imports)
    fi

    if [ "$ALL_FILES_MODE" -eq 0 ]; then
        # Scope errors to only the changed files; suppress noise from
        # transitively imported upstream modules with pre-existing debt.
        MYPY_ARGS+=(--follow-imports=silent)
    fi

    # Filter out files that are excluded in mypy.ini. When mypy is given an
    # explicit file list it ignores the [mypy] exclude setting, so we strip
    # them here to match what CI sees (only the files we actually wrote/changed
    # that are not covered by the upstream debt exclusions).
    FILTERED_TARGETS=()
    for f in "${MYPY_TARGETS[@]}"; do
        # Normalise to forward-slash relative path
        rel="${f#./}"
        skip=0
        for pattern in \
            "bottles/backend/managers/dependency.py" \
            "bottles/backend/managers/installer.py" \
            "bottles/backend/managers/manager.py" \
            "bottles/backend/managers/versioning.py" \
            "bottles/backend/managers/ubisoftconnect.py" \
            "bottles/backend/managers/template.py" \
            "bottles/backend/managers/origin.py" \
            "bottles/backend/managers/component.py" \
            "bottles/backend/managers/repository.py" \
            "bottles/backend/managers/library.py" \
            "bottles/backend/managers/steam.py" \
            "bottles/backend/managers/backup.py" \
            "bottles/backend/managers/eagle.py" \
            "bottles/backend/wine/regkeys.py" \
            "bottles/backend/wine/executor.py" \
            "bottles/backend/wine/winecommand.py" \
            "bottles/backend/models/samples.py" \
            "bottles/backend/models/config.py" \
            "bottles/backend/utils/vulkan.py" \
            "bottles/backend/utils/generic.py" \
            "bottles/backend/utils/connection.py" \
            "bottles/backend/utils/manager.py" \
            "bottles/backend/logger.py" \
            "bottles/backend/managers/playtime.py" \
            "bottles/fvs/repo.py" \
            "bottles/frontend/views/bottle_details.py" \
            "bottles/frontend/views/bottle_versioning.py" \
            "bottles/frontend/views/bottle_installers.py" \
            "bottles/frontend/views/bottle_preferences.py" \
            "bottles/frontend/views/bottle_dependencies.py" \
            "bottles/frontend/views/details.py" \
            "bottles/frontend/views/eagle.py" \
            "bottles/frontend/views/list.py" \
            "bottles/frontend/views/preferences.py" \
            "bottles/frontend/views/new_bottle_dialog.py" \
            "bottles/frontend/widgets/library.py" \
            "bottles/frontend/operation.py" \
            "bottles/tests/backend/integration/playtime/conftest.py" \
        ; do
            if [[ "$rel" == "$pattern" || "$rel" == bottles/backend/repos/* || "$rel" == bottles/backend/dlls/* || "$rel" == bottles/frontend/windows/* ]]; then
                skip=1
                break
            fi
        done
        [ "$skip" -eq 0 ] && FILTERED_TARGETS+=("$f")
    done

    if [ ${#FILTERED_TARGETS[@]} -eq 0 ]; then
        echo ""
        echo "    All changed files are in the upstream-debt exclusion list -- mypy skipped."
    else
        run_check "mypy (${#FILTERED_TARGETS[@]} file(s))" \
            "$VENV_PATH/bin/mypy" "${MYPY_ARGS[@]}" "${FILTERED_TARGETS[@]}"
    fi
fi

# ---------------------------------------------------------------------------
# 8. Summary
# ---------------------------------------------------------------------------
echo ""
if [ "$OVERALL" -eq 0 ]; then
    echo "============================================="
    echo "  All checks passed."
    echo "============================================="
else
    echo "============================================="
    echo "  One or more checks FAILED. See output above."
    echo "============================================="
fi

exit "$OVERALL"
