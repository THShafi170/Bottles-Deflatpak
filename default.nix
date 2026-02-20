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
let
  bottles-deflatpak = pkgs.callPackage ./nix/fhsenv.nix {
    inherit bottles-deflatpak-unwrapped;
    inherit (pkgs) vkbasalt umu-launcher;
    obs-vkcapture = pkgs.obs-studio-plugins.obs-vkcapture;
  };
in
bottles-deflatpak
// {
  unwrapped = bottles-deflatpak-unwrapped;
  # For better CLI experience with nix-build -A:
  bottles-deflatpak = bottles-deflatpak;
  bottles-deflatpak-unwrapped = bottles-deflatpak-unwrapped;
}
