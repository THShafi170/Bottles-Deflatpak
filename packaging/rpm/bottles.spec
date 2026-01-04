Name:       bottles
Epoch:      2
Version:    60.1
Release:    %autorelease
Summary:    Run Windows in a Bottle (Native Deflatpak version)

%global forgeurl https://github.com/tenshou170/Bottles-Deflatpak
%global tag v%{version}
%forgemeta

# The following two files are licensed as MIT:
# bottles/backend/models/vdict.py
# bottles/backend/utils/vdf.py
License:    GPL-3.0-or-later AND MIT
URL:        %{forgeurl}
Source0:    %{forgesource}

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
Requires:       glibc(x86-32)           %dnl # https://github.com/bottlesdevs/Bottles/issues/601#issuecomment-936772762
Requires:       gtk4
Requires:       gtksourceview5
Requires:       hicolor-icon-theme
Requires:       libadwaita >= 1.1.99
Requires:       p7zip p7zip-plugins     %dnl # needed by the dependencies manager
Requires:       patool
Requires:       xdpyinfo                %dnl # needed by the display util
Requires:       ImageMagick             %dnl # https://bugzilla.redhat.com/show_bug.cgi?id=2227538

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
Requires:       python3dist(fvs)
Requires:       python3dist(orjson)
Requires:       python3dist(pycairo)
Requires:       python3dist(pygobject)
Requires:       python3dist(charset-normalizer)
Requires:       python3dist(idna)
Requires:       python3dist(urllib3)
Requires:       python3dist(certifi)
Requires:       python3dist(pefile)
Requires:       python3dist(vkbasalt-cli)

# Optional dependencies which may be required for running 32-bit bottles.
# We recommend those in order to allow users to opt out.
Recommends:     freetype.i686
Recommends:     mesa-dri-drivers.i686
Recommends:     mesa-filesystem.i686
Recommends:     mesa-libEGL.i686
Recommends:     mesa-libgbm.i686
Recommends:     mesa-libglapi.i686
Recommends:     mesa-libGL.i686
Recommends:     mesa-libGLU.i686
Recommends:     mesa-va-drivers.i686
Recommends:     mesa-vulkan-drivers.i686
Recommends:     SDL2.i686
Recommends:     vulkan-loader.i686

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
Recommends:     bubblewrap


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
%find_lang %{name}


%check
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/*.xml
desktop-file-validate %{buildroot}%{_datadir}/applications/*.desktop


%files -f %{name}.lang
%license COPYING.md
%doc README.md
%{_bindir}/%{name}
%{_bindir}/%{name}-cli
%{_datadir}/%{name}/
%{_datadir}/applications/*.desktop
%{_datadir}/glib-2.0/schemas/*.gschema.xml
%{_datadir}/icons/hicolor/*/apps/*.svg
%{_metainfodir}/*.xml


%changelog
%autochangelog
