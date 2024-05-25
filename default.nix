{
  lib,
  dream2nix,
  ...
}: {
  imports = [
    dream2nix.modules.dream2nix.WIP-python-pdm
  ];

  deps = {nixpkgs, ...}: {
    pkgs = nixpkgs;
    python = nixpkgs.python3;
  };

  mkDerivation = {
    src = lib.cleanSourceWith {
      src = lib.cleanSource ./.;
      filter = name: type:
        !(builtins.any (x: x) [
          (lib.hasSuffix ".nix" name)
          (lib.hasPrefix "." (builtins.baseNameOf name))
          (lib.hasSuffix "flake.lock" name)
        ]);
    };
  };

  pdm.lockfile = ./pdm.lock;
  pdm.pyproject = ./pyproject.toml;

  buildPythonPackage = {
    pythonImportsCheck = [
      "jsonpath"
    ];
  };
}
