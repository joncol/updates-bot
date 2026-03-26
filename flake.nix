{
  description = "Weekly changelog reporter for Slack";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python312;
      in
      {
        devShells.default = pkgs.mkShell {
          packages = [
            python
            pkgs.git
          ];

          shellHook = ''
            if [ ! -d .venv ]; then
              python -m venv .venv
              .venv/bin/pip install -q -r requirements.txt
            fi
            source .venv/bin/activate
          '';
        };

        packages.default = pkgs.writeShellScriptBin "updates-bot" ''
          exec ${python}/bin/python ${self}/main.py "$@"
        '';
      });
}
