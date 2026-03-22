{
  pkgs ? import <nixpkgs> { },
}:

let
  version = pkgs.lib.removeSuffix "\n" (builtins.readFile ./VERSION);
  src = ./.;

  bottles-deflatpak-unwrapped = pkgs.callPackage ./nix/package.nix {
    inherit version src;
    inherit (pkgs) file kmod;
    obs-vkcapture = pkgs.obs-studio-plugins.obs-vkcapture;
  };
in
pkgs.mkShell {
  name = "bottles-deflatpak-dev";
  inputsFrom = [ bottles-deflatpak-unwrapped ];
  nativeBuildInputs = with pkgs; [
    meson
    ninja
    blueprint-compiler
    pkg-config
    python3
    wrapGAppsHook4
    gtk4
    libadwaita
    appstream-glib
    desktop-file-utils
  ];
}
