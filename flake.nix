{
  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        name = "antlr4-python-grun";
        name-shell = "${name}-shell";
      in
        {
          packages.${name} = pkgs.poetry2nix.mkPoetryApplication {
            projectDir = ./.;
          };
          packages.${name-shell} = pkgs.mkShell {
            buildInputs = [
              (pkgs.poetry2nix.mkPoetryEnv {
                projectDir = ./.;
              })
              pkgs.poetry
              pkgs.antlr4
              pkgs.jdk8
            ];
          };
          devShell = self.packages.${system}.${name-shell};
          defaultPackage = self.packages.${system}.${name};
          defaultApp = self.packages.${system}.${name};
        }
    );
}
