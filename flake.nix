{
  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        name = "antlr4-python-grun";
      in
        {
        packages.${name} = pkgs.poetry2nix.mkPoetryApplication {
          projectDir = ./.;
        };
        devShell = pkgs.mkShell {
          buildInputs = [
            (pkgs.poetry2nix.mkPoetryEnv {
              projectDir = ./.;
            })
            pkgs.poetry
            pkgs.antlr4
            pkgs.jdk8
          ];
        };
        defaultPackage = self.packages.${system}.${name};
        defaultApp = self.packages.${system}.${name};
        }
    );
}
