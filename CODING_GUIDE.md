# Coding Guide

## Build & Run locally

### Build & Install

```bash
meson setup build --prefix=/usr
meson compile -C build
sudo meson install -C build
```

### Run

```bash
bottles
```

### Uninstall

```bash
sudo ninja -C build uninstall
```

## Pre-Commit Checks

Run all linters and formatters before committing:

```bash
./venv/bin/python -m pre_commit run --all-files
```

This runs: `ruff`, `ruff-format`, `mypy`, `autoflake`, and various file checks.

## Unit Tests

```bash
./venv/bin/python -m pytest bottles/tests/ -v
```

> **Note:** Tests that import GTK/GI modules require system GObject Introspection typelibs to be available.

## I18n Files

### `po/POTFILES`

List of source files containing translatable strings.
Regenerate this file when you add/move/remove/rename files
that contain translatable strings.

```bash
cat > po/POTFILES <<EOF
# List of source files containing translatable strings.
# Please keep this file sorted alphabetically.
EOF
grep -rlP "_\(['\"]" bottles | sort >> po/POTFILES
cat >> po/POTFILES <<EOF
data/com.usebottles.bottles.desktop.in.in
data/com.usebottles.bottles.gschema.xml
data/com.usebottles.bottles.metainfo.xml.in.in
EOF
```

### `po/bottles.pot` and `po/*.po`

We have a main `.pot` file which is a template for the `.po` files.
For each language listed in `po/LINGUAS` there is a corresponding `.po` file.
Regenerate these when any translatable string is added/changed/removed:

```bash
# make sure you have `meson` and `blueprint-compiler` installed
meson setup /tmp/i18n-build
meson compile -C /tmp/i18n-build/ bottles-pot
meson compile -C /tmp/i18n-build/ bottles-update-po
```
