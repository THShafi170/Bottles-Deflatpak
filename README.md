<div align="center">
  <img src="https://raw.githubusercontent.com/bottlesdevs/Bottles/main/data/icons/hicolor/scalable/apps/com.usebottles.bottles.svg" width="64">
  <h1 align="center">Bottles (Native Deflatpak)</h1>
  <p align="center">Run Windows Software on Linux - Distro-Agnostic & Native</p>
</div>

<br/>

<div align="center">
  <a href="https://github.com/tenshou170/Bottles-Deflatpak/releases">
    <img alt="GitHub Releases" src="https://img.shields.io/github/v/release/tenshou170/Bottles-Deflatpak" />
  </a>
  <a href="https://github.com/tenshou170/Bottles-Deflatpak/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-GPL--3.0-blue.svg">
  </a>
</div>

<br/>

# What is "Deflatpak"?

This project is a fork of [Bottles](https://usebottles.com) that removes all Flatpak-specific dependencies, restrictions, and sandboxing. It is designed to run **natively** on your host Linux system.

## Differences from Upstream

| Feature | Upstream (Official Bottles) | Bottles Deflatpak (This Fork) |
| :--- | :--- | :--- |
| **Distribution** | Flatpak (Sandboxed) | Native Packages (DEB, RPM, AUR, Tarball) |
| **File Access** | Restricted (Permissions required) | **Full Access** (Optional Sandbox available) |
| **Sandboxing** | Flatpak (Hardcoded) | **Optional** (Bubblewrap-based) |
| **Dependencies** | Bundled in Flatpak Runtime | Uses System Libraries (glibc, gtk4, python, etc.) |
| **Integration** | Portals required for some interactions | Native Host Integration |
| **Size** | Large (Bundles Runtimes) | Small (Uses System Resources) |

> [!WARNING]
> By default, this version runs without a sandbox. **Windows executables have full access to your personal files and system.** You can enable the **Dedicated Sandbox** in Bottle Preferences to restrict access using `bubblewrap`. See [SECURITY.md](SECURITY.md) for more details.

## Installation

### AUR (Arch Linux)
The `PKGBUILD` is available in `packaging/aur/`.
```bash
cd packaging/aur
makepkg -si
```

### RPM (Fedora/RHEL)
```bash
rpmbuild -bb packaging/rpm/bottles.spec
```

### DEB (Debian/Ubuntu)
```bash
cd packaging/deb
dpkg-buildpackage -us -uc -b
```

### Binary Pack (Generic Linux)
We provide a distro-agnostic `tar.gz` binary pack in the Releases.
Simply extract and run:
```bash
./build-packages.sh # to build locally
```
Then run the executable in `bottles/` or install it to your system.

## Building from Source

### Dependencies
Ensure you have the following installed on your host system:
- `meson`
- `ninja`
- `blueprint-compiler`
- `python3` (and modules listed in `requirements.txt`)
- `libadwaita-1`
- `gtk4`
- `cabextract`, `patool`, `7zip` (runtime dependencies)

### Build
```bash
meson setup build --prefix=/usr
ninja -C build
sudo ninja -C build install
```

## Credits
Based on the amazing work by the [Bottles Developers](https://usebottles.com).
Code of Conduct follows the [GNOME Code of Conduct](https://wiki.gnome.org/Foundation/CodeOfConduct).
