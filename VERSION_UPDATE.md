# Version Update Guide

## Paths to be updated on version change

- `VERSION` (the source of truth)
- `meson.build`
- `data/com.usebottles.bottles.metainfo.xml.in.in`
- `nix/package.nix` (if not reading from VERSION)
- `bottles/frontend/params.py` (check if versions are hardcoded)
- `packaging/rpm/bottles.spec`
- `packaging/deb/debian/changelog`
