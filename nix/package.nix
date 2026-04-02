{
  lib,
  python3Packages,
  blueprint-compiler,
  meson,
  ninja,
  pkg-config,
  wrapGAppsHook4,
  appstream-glib,
  desktop-file-utils,
  librsvg,
  gtk4,
  gtksourceview5,
  libadwaita,
  cabextract,
  p7zip,
  xdpyinfo,
  imagemagick,
  lsb-release,
  pciutils,
  procps,
  gamemode,
  gamescope,
  mangohud,
  vkbasalt-cli,
  vmtouch,
  libportal,
  bubblewrap,
  umu-launcher,
  file,
  kmod,
  obs-vkcapture,
  src,
  version,
}:

python3Packages.buildPythonApplication {
  pname = "bottles-deflatpak-unwrapped";
  inherit version src;

  # Note: Flatpak-specific patches from upstream nixpkgs are skipped because
  # this fork (Bottles-Deflatpak) already removes sandbox assumptions.

  nativeBuildInputs = [
    blueprint-compiler
    meson
    ninja
    pkg-config
    wrapGAppsHook4
    gtk4 # gtk4-update-icon-cache
    appstream-glib
    desktop-file-utils
  ];

  buildInputs = [
    librsvg
    gtk4
    gtksourceview5
    libadwaita
    libportal
  ];

  propagatedBuildInputs =
    with python3Packages;
    [
      pyyaml
      pycurl
      chardet
      requests
      markdown
      icoextract
      patool
      pathvalidate
      fvs
      orjson
      pycairo
      pygobject3
      charset-normalizer
      idna
      urllib3
      certifi
      pefile
      yara-python
    ]
    ++ [
      cabextract
      p7zip
      xdpyinfo
      imagemagick
      vkbasalt-cli
      bubblewrap
      umu-launcher
      file
      kmod
      obs-vkcapture

      gamemode
      gamescope
      mangohud
      vmtouch

      # subprocess.Popen() dependencies
      lsb-release
      pciutils
      procps
    ];

  pyproject = false;
  dontWrapGApps = true; # prevent double wrapping

  preFixup = ''
    makeWrapperArgs+=("''${gappsWrapperArgs[@]}")
  '';

  meta = {
    description = "Easy-to-use wineprefix manager (Fork with Flatpak-specific dependencies removed)";
    homepage = "https://github.com/THShafi170/Bottles-Deflatpak";
    license = lib.licenses.gpl3Only;
    platforms = lib.platforms.linux;
    mainProgram = "bottles";
  };
}
