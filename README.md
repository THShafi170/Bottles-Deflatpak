<div align="center">
  <img src="https://raw.githubusercontent.com/bottlesdevs/Bottles/main/data/icons/hicolor/scalable/apps/com.usebottles.bottles.svg" width="64">
  <h1 align="center">Bottles (Deflatpak)</h1>
  <p align="center">Run Windows Software on Linux — Natively, without Flatpak</p>
</div>

<br/>

<div align="center">
  <a href="https://github.com/THShafi170/Bottles-Deflatpak/blob/main/COPYING.md">
    <img src="https://img.shields.io/badge/License-GPL--3.0-blue.svg">
  </a>

  <hr />

<a href="https://docs.usebottles.com">Upstream Documentation</a> ·
<a href="https://github.com/THShafi170/Bottles-Deflatpak/issues">Issues</a>

</div>

<br/>

![Bottles Dark](docs/screenshot-dark.png#gh-dark-mode-only)![Bottles Light](docs/screenshot-light.png#gh-light-mode-only)

## About

**Bottles-Deflatpak** is a fork of [Bottles](https://github.com/bottlesdevs/Bottles) with all Flatpak-specific dependencies and sandbox assumptions removed. It builds and runs natively on any Linux distribution using standard system packages and Meson.

### Key Distinctions

#### 🏗️ Architecture: True Native Execution

Unlike upstream, this fork is stripped of all Flatpak assumptions. It uses your system's libraries and runners directly, eliminating container overhead and `FLATPAK_ID` dependency checks.

#### 🛡️ Security: Hardened Native Sandboxing

We've replaced the standard container model with a **deny-by-default** sandbox powered by `bubblewrap`. You have granular control over what resources (GPU, Display, Sound, Network) are shared with your Windows applications.

#### 🎮 Compatibility: Modernized Proton Support

Integration with `umu-launcher` and official `proton` scripts ensures your games run in a Steam-accurate environment with full `protonfixes` support, regardless of how they were installed.

#### 📦 Distribution: Distro-Agnostic Packaging

Builds directly with Meson/Ninja. Native packaging files are included for:

- **Fedora/RHEL** (RPM)
- **Debian/Ubuntu** (DEB)
- **Arch Linux** (AUR/PKGBUILD)
- **Universal** (distro-agnostic tarball)

## Installation

### From source

See [Building](#building) below.

### Distribution packages

Pre-made packaging files are included for several distributions:

| Distribution    | Format   | Path                               |
| --------------- | -------- | ---------------------------------- |
| Fedora / RHEL   | RPM      | [`packaging/rpm/`](packaging/rpm/) |
| Debian / Ubuntu | DEB      | [`packaging/deb/`](packaging/deb/) |
| Arch Linux      | PKGBUILD | [`packaging/aur/`](packaging/aur/) |

You can also use `build-packages.sh` to produce an installable tarball:

```bash
./build-packages.sh
```

## Building

### Prerequisites

- `meson` and `ninja`
- `blueprint-compiler`
- GTK 4, libadwaita (≥ 1.2), and GtkSourceView 5 development packages
- Python 3 with the dependencies listed in `requirements.txt`
- `cabextract`, `p7zip`, `xdpyinfo`, `ImageMagick`
- `bubblewrap` (optional, for hardened sandboxing)
- `umu-launcher` (optional, for enhanced Proton support)

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

## Contributing

Refer to the [Contributing Guide](CONTRIBUTING.md) and [Coding Guide](CODING_GUIDE.md).

## Upstream

This fork tracks [bottlesdevs/Bottles](https://github.com/bottlesdevs/Bottles). Upstream documentation is available at [docs.usebottles.com](https://docs.usebottles.com).

## License

Bottles-Deflatpak is licensed under the [GPL-3.0](COPYING.md). Some vendored utilities are licensed under MIT — see file headers for details.
