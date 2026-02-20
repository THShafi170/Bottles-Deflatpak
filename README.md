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
<a href="#nix--nixos">Nix/NixOS Documentation</a> ·
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
- **Arch Linux** (PKGBUILD/ZST)
- **Nix / NixOS** (Flake & Legacy)
- **Universal** (distro-agnostic tarball)

## Installation

### From source

See [Building](#building) below.

### Distribution packages

Pre-made packaging files are included for several distributions:

| Distribution | Binary / Source | Path / Link |
| :--- | :--- | :--- |
| Universal | .tar.gz | [GitHub Releases](https://github.com/THShafi170/Bottles-Deflatpak/releases) |
| Arch Linux | .pkg.tar.zst | [GitHub Releases](https://github.com/THShafi170/Bottles-Deflatpak/releases) / [AUR](packaging/aur/) |
| Debian / Ubuntu | .deb | [GitHub Releases](https://github.com/THShafi170/Bottles-Deflatpak/releases) / [Source](packaging/deb/) |
| Fedora / RHEL | .rpm | [GitHub Releases](https://github.com/THShafi170/Bottles-Deflatpak/releases) / [Spec](packaging/rpm/) |
| Nix / NixOS (Flake) | Flake | [flake.nix](flake.nix) |
| Nix / NixOS (Legacy) | Default | [default.nix](default.nix) |


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

## Nix / NixOS

If you use Nix or NixOS, this repository includes a Flake for easy installation and development.

> [!TIP]
> **NixOS Users:** Using the Nix Flake is the recommended way to install this fork of Bottles. It provides a reproducible environment with all dependencies automatically managed.

### Run directly

```bash
nix run github:THShafi170/Bottles-Deflatpak
```

### Install using Flakes

Add this repository to your flake inputs:

```nix
{
  inputs.bottles-deflatpak.url = "github:THShafi170/Bottles-Deflatpak";
  # ...
  outputs = { self, nixpkgs, bottles-deflatpak, ... }: {
    # ...
    environment.systemPackages = [
      # Recommended: FHS wrapped version for better Wine compatibility
      bottles-deflatpak.packages.${pkgs.system}.bottles-deflatpak

      # Alternatively: Unwrapped version (standard package)
      # bottles-deflatpak.packages.${pkgs.system}.bottles-deflatpak-unwrapped
    ];
  };
}
```

The `bottles-deflatpak` package (also available as `default`) is wrapped in an **FHS (Filesystem Hierarchy Standard) environment**. This is highly recommended as it provides the necessary 32-bit and 64-bit libraries that Wine/Proton runners expect.

### Development Shell

```bash
nix develop
```

### Legacy / Non-Flakes

If you don't use Flakes, you can still build and run this fork using the provided `default.nix` and `shell.nix`.

#### Build

```bash
# Build the recommended (wrapped) version
nix-build

# Build the unwrapped version explicitly
nix-build -A bottles-deflatpak-unwrapped
```

#### Nix-shell

```bash
nix-shell
```

### Cachix Binary Cache

If you want to speed up your Nix builds and reduce compilation time (especially for dependencies or the FHS environment), you can use the community binary cache.

#### Consuming the cache

If you are using NixOS, add the following to your configuration:

```nix
{
  nix.settings = {
    substituters = [ "https://bottles-deflatpak.cachix.org" ];
    trusted-public-keys = [ "bottles-deflatpak.cachix.org-1:YT/o8RO4yysuReUamuL09Db+O7PA5FtsYqeRXSfbweE=" ];
  };
}
```

Or just use the Cachix CLI:

```bash
cachix use bottles-deflatpak
```

## Contributing

Refer to the [Contributing Guide](CONTRIBUTING.md) and [Coding Guide](CODING_GUIDE.md).

The included GitHub Actions workflow will compile and upload the binaries to automatically make a release. For Cachix setup instructions for Nix/NixOS, see the [GitHub Actions & Nix (Cachix)](CONTRIBUTING.md#github-actions--nix-cachix) section in the contributing guide.

## Upstream

This fork tracks [bottlesdevs/Bottles](https://github.com/bottlesdevs/Bottles). Upstream documentation is available at [docs.usebottles.com](https://docs.usebottles.com).

## License

Bottles-Deflatpak is licensed under the [GPL-3.0](COPYING.md). Some vendored utilities are licensed under MIT — see file headers for details.
