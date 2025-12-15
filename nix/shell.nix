{pkgs, lib, config, ...}:
let
  py = pkgs.python313Packages;
  ctransformers = py.buildPythonPackage rec {
    pname = "ctransformers";
    version = "0.2.27";
    pyproject = true;
    src = pkgs.fetchPypi {
      inherit pname version;
      sha256 = "sha256-JWU9S+il7U4tN1ZUTB6Ygb+VQEvlNxw+1QaiVsKGY9U=";
    };
    build-system = with py; [
      scikit-build
      setuptools
      wheel
      ninja
      cmake
    ];
    propagatedBuildInputs = with py; [
      huggingface-hub
      py-cpuinfo
    ];
    dontUseCmakeConfigure = true;
    dontUseNinjaBuild = true;
    dontUseNinjaInstall = true;
  };
in {
  devShells.default = pkgs.mkShell {
    name = "unnamed (1.0.0) devshell";
    packages = (with py; [
      langchain-community
      setuptools
      langchain
      python
      flake8
      wheel
      pip
    ]) ++ ([
      ctransformers
    ]);
  };
}