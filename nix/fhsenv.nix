{
  buildFHSEnv,
  symlinkJoin,
  bottles-deflatpak-unwrapped,
  vkbasalt,
  obs-vkcapture,
  umu-launcher,
  extraPkgs ? pkgs: [ ],
  extraLibraries ? pkgs: [ ],
}:

let
  fhsEnv = {
    inherit (bottles-deflatpak-unwrapped) version;
    # Many WINE games need 32bit
    multiArch = true;

    targetPkgs =
      pkgs:
      [
        bottles-deflatpak-unwrapped
        # This only allows to enable the toggle, vkBasalt won't work if not
        # installed with environment.systemPackages (or nix-env)
        # See https://github.com/bottlesdevs/Bottles/issues/2401
        vkbasalt
        umu-launcher
      ]
      ++ extraPkgs pkgs;

    multiPkgs =
      let
        xorgDeps =
          pkgs: with pkgs; [
            libpthread-stubs
            libsm
            libx11
            libxaw
            libxcb
            libxcomposite
            libxcursor
            libxdmcp
            libxext
            libxi
            libxinerama
            libxmu
            libxrandr
            libxrender
            libxv
            libxxf86vm
          ];
        gstreamerDeps =
          pkgs: with pkgs.gst_all_1; [
            gstreamer
            gst-plugins-base
            gst-plugins-good
            gst-plugins-ugly
            gst-plugins-bad
            gst-libav
          ];
        waylandDeps =
          pkgs: with pkgs; [
            libxkbcommon
            wayland
          ];
      in
      pkgs:
      with pkgs;
      [
        # https://wiki.winehq.org/Building_Wine
        alsa-lib
        cups
        dbus
        fontconfig
        freetype
        glib
        gnutls
        libglvnd
        gsm
        libgphoto2
        libjpeg_turbo
        libkrb5
        libpcap
        libpng
        libpulseaudio
        libtiff
        libunwind
        libusb1
        libv4l
        libxml2
        mpg123
        ocl-icd
        openldap
        samba4
        sane-backends
        SDL2
        udev
        vulkan-loader
        libglvnd

        # Visual Tools
        vkbasalt
        obs-vkcapture

        # https://www.gloriouseggroll.tv/how-to-get-out-of-wine-dependency-hell/
        alsa-plugins
        dosbox
        giflib
        gtk3
        libva
        libxslt
        ncurses
        openal

        # Steam runtime
        libgcrypt
        libgpg-error
        p11-kit
        zlib # Freetype
      ]
      ++ xorgDeps pkgs
      ++ gstreamerDeps pkgs
      ++ extraLibraries pkgs
      ++ waylandDeps pkgs;
  };
in
symlinkJoin {
  pname = "bottles-deflatpak";
  paths = [
    (buildFHSEnv (
      fhsEnv
      // {
        pname = "bottles-deflatpak";
        runScript = "bottles";
      }
    ))
    (buildFHSEnv (
      fhsEnv
      // {
        pname = "bottles-deflatpak-cli";
        runScript = "bottles-cli";
      }
    ))
  ];
  postBuild = ''
    mkdir -p $out/share
    ln -s ${bottles-deflatpak-unwrapped}/share/applications $out/share
    ln -s ${bottles-deflatpak-unwrapped}/share/icons $out/share
  '';

  inherit (bottles-deflatpak-unwrapped) meta version;
}
