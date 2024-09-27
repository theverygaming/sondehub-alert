{
  description = "sondehub-alert";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/release-24.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        pysondehub = pkgs.python312Packages.buildPythonPackage rec {
          pname = "sondehub";
          version = "0.3.2";
          pyproject = true;

          build-system = [
            pkgs.python312Packages.poetry-core
          ];

          dependencies = [
            pkgs.python312Packages.boto3
            pkgs.python312Packages.paho-mqtt
            pkgs.python312Packages.dateutil
            pkgs.python312Packages.requests
            pkgs.python312Packages.geopy
          ];

          src = pkgs.fetchPypi {
            inherit pname version;
            hash = "sha256-zShcqQ55HmCOgOU0xP/uZtWJEzY9fj5yqpCq2Tfn1UQ=";
          };
        };
        pythonDeps = [
          pkgs.python312Packages.python-telegram-bot
          pysondehub
        ];
      in
      rec {
        devShell = pkgs.mkShell {
          name = "sondehub-alert";
          nativeBuildInputs = [ pkgs.python312 ] ++ pythonDeps;
        };

        defaultPackage = pkgs.python312Packages.buildPythonPackage rec {
          pname = "sondehub-alert";
          version = "0.0.1";
          pyproject = true;

          build-system = [
            pkgs.python312Packages.setuptools
          ];

          dependencies = pythonDeps;

          makeWrapperArgs = ["--set SSL_CERT_FILE ${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"];

          src = ./.;
        };
      }
    );
}
