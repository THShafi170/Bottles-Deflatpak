{
  description = "Bottles (Deflatpak) - Run Windows Software on Linux natively, without Flatpak";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      ...
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        version = nixpkgs.lib.removeSuffix "\n" (builtins.readFile ./VERSION);

        bottles-deflatpak-unwrapped = pkgs.callPackage ./nix/package.nix {
          inherit version;
          src = self;
          inherit (pkgs) file kmod;
          obs-vkcapture = pkgs.obs-studio-plugins.obs-vkcapture;
        };
      in
      {
        packages = {
          bottles-deflatpak-unwrapped = bottles-deflatpak-unwrapped;
          bottles-deflatpak = pkgs.callPackage ./nix/fhsenv.nix {
            inherit bottles-deflatpak-unwrapped;
            inherit (pkgs) vkbasalt umu-launcher;
            obs-vkcapture = pkgs.obs-studio-plugins.obs-vkcapture;
          };
          default = self.packages.${system}.bottles-deflatpak;
        };

        devShells.default = pkgs.mkShell {
          name = "bottles-deflatpak-dev";
          nativeBuildInputs = with pkgs; [
            pkgs.cachix
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
          buildInputs =
            bottles-deflatpak-unwrapped.buildInputs ++ bottles-deflatpak-unwrapped.propagatedBuildInputs;
        };
      }
    );
}
