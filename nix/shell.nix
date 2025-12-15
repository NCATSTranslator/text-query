{pkgs, lib, config, ...}:
let
  py = pkgs.python313Packages;
in {
  devShells.default = pkgs.mkShell {
    name = "unnamed (1.0.0) devshell";
    packages = with py; [
      langchain-community
      setuptools
      python
      flake8
      wheel
      pip
    ];
  };
}