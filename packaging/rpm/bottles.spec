Name:       bottles-deflatpak
Version:    67.0
Release:    1
Summary:    Run Windows in a Bottle (native fork, no Flatpak)
Provides:   bottles = %{version}-%{release}
Conflicts:  bottles
Obsoletes:  bottles < %{version}-%{release}

# The following two files are licensed as MIT:
# bottles/backend/models/vdict.py
# bottles/backend/utils/vdf.py
License:    GPL-3.0-or-later AND MIT
URL:        https://github.com/Tenshou170/Bottles-Deflatpak
Source0:    bottles-v%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib
BuildRequires:  meson
BuildRequires:  python3-devel
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(gtk4)
BuildRequires:  pkgconfig(libadwaita-1) >= 1.1.99
BuildRequires:  blueprint-compiler

Requires:       cabextract
Requires:       gtk4
Requires:       gtksourceview5
Requires:       hicolor-icon-theme
Requires:       libadwaita >= 1.1.99
Requires:       7zip                    %dnl # needed for archive extraction (7z)
Requires:       patool
Requires:       xdpyinfo                %dnl # needed by the display util
Requires:       ImageMagick             %dnl # needed for icon conversion
Requires:       libportal-gtk4
Requires:       bubblewrap              %dnl # needed for native sandboxing
Requires:       umu-launcher            %dnl # needed for UMU support
# fvs2 is the versioning backend (Go binary). It is not yet in Fedora/RHEL
# repositories; install it manually from https://github.com/fvs-lab/fvs2
# Versioning will be unavailable without it but the rest of Bottles works fine.
# Recommends: fvs2

# Use `generate_requires.sh` to generate Python runtime dependencies
# using upstream's `requirements.txt`, which is included in the tarball,
# but not used by Meson.
Requires:       python3dist(pyyaml)
Requires:       python3dist(pycurl)
Requires:       python3dist(chardet)
Requires:       python3dist(requests)
Requires:       python3dist(markdown)
Requires:       python3dist(icoextract)
Requires:       python3dist(patool)
Requires:       python3dist(pathvalidate)
Requires:       python3dist(pefile)
Requires:       python3dist(vkbasalt-cli)
Requires:       python3dist(yara-python)

# Optional dependencies which may be required for running 32-bit bottles.
# We recommend those in order to allow users to opt out.
Recommends:     freetype
Recommends:     mesa-dri-drivers
Recommends:     mesa-filesystem
Recommends:     mesa-libEGL
Recommends:     mesa-libgbm
Recommends:     mesa-libglapi
Recommends:     mesa-libGL
Recommends:     mesa-libGLU
Recommends:     mesa-va-drivers
Recommends:     mesa-vulkan-drivers
Recommends:     SDL2
Recommends:     vulkan-loader

# Optional dependencies that will provide extra features in Bottles
# when installed.
Recommends:     gamemode
Recommends:     gamescope
Recommends:     mangohud
# Since this pulls in OBS Studio and is not generally required for gaming
# setups, we only suggest.
Suggests:       obs-studio-plugin-vkcapture
Recommends:     vkBasalt
Recommends:     vmtouch
Recommends:     pciutils
Recommends:     vulkan-tools


%description
Bottles lets you run Windows software on Linux, such as applications
and games. It introduces a workflow that helps you organize by
categorizing each software to your liking. Bottles provides several
tools and integrations to help you manage and optimize your
applications.

Features:

- Use pre-configured environments as a base
- Change runners for any bottle
- Various optimizations and options for gaming
- Repair in case software or bottle is broken
- Install various known dependencies
- Integrated task manager to manage and monitor processes
- Backup and restore

%prep
%autosetup -n Bottles-Deflatpak-%{version} -p1


%build
%meson
%meson_build


%install
%meson_install
# The gettext domain is 'com.usebottles.bottles'
%find_lang com.usebottles.bottles


%check
appstream-util validate-relax --nonet %buildroot%_metainfodir/*.xml
desktop-file-validate %buildroot%_datadir/applications/*.desktop


%files -f com.usebottles.bottles.lang
%license COPYING.md
%doc README.md
%{_bindir}/bottles
%{_bindir}/bottles-cli
%{_datadir}/bottles/
%{_datadir}/applications/*.desktop
%{_datadir}/glib-2.0/schemas/*.gschema.xml
%{_datadir}/icons/hicolor/*/apps/*.svg
%{_datadir}/licenses/com.usebottles.bottles/
%{_metainfodir}/*.xml


%changelog
* Mon Aug 31 2026 Tenshou Zmeyev <tenshou170@gmail.com> - 67.0-1
- Sync with upstream 67.0
- Enabled Soda 11.0-7 with Adaptive Launch sessions and host OpenXR
- Added ProtoSoda 11.0-2 with Adaptive Launch support through UMU
- Added ARM64 Soda runner selection through the component catalog
- Added single action for adding/removing programs from Library
- Sorted Library entries by name
- Pure native execution for Bottles on Linux & NixOS without Flatpak overhead

* Mon Aug 31 2026 Tenshou Zmeyev <tenshou170@gmail.com> - 66.10-1
- Sync with upstream 66.10
- Add Run dialogue command to Legacy Wine Tools
- Fix Chrome/Chromium browser handover crash
- Pure native execution with enhanced NixOS and driver support

* Tue Jun 02 2026 Tenshou Zmeyev <tenshou170@gmail.com> - 64.1-1
- Sync with upstream 64.1
- Eagle malware/stealer scanner with crash-detection prompt
- Bulk bottle component update dialog
- Dynamic sandbox guard for programs outside the bottle prefix
- NTsync support (kernel /dev/ntsync + Wine >= 10)
- winebridge update dialog on startup
- Various upstream bugfixes

* Thu Apr 02 2026 Tenshou Zmeyev <tenshou170@gmail.com> - 63.2-1
- Sync with upstream 63.2 base
- Deep nativization: optimized hardware discovery and native path discovery
- Enhanced bwrap sandbox with D-Bus and theme integration
- Prioritize native Steam installations over Flatpak

* Wed Mar 25 2026 Tenshou Zmeyev <tenshou170@gmail.com> - 63.0-1
- Sync with upstream 63.0
- Refined native compatibility, no more Flatpak extensions logic
- Integrated NixOS patches directly into the code
- Robust terminal quoting and desktop entry portal support

* Mon Feb 23 2026 Tenshou Zmeyev <tenshou170@gmail.com> - 62.0-1
- Universal RPM package (distro-agnostic)
