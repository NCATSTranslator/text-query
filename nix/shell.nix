{pkgs, lib, config, ...}:
let
  py = pkgs.python313Packages;
  ctransformers = py.buildPythonPackage rec {
    pname = "ctransformers";
    version = "0.2.27";
    format = "wheel";
    src = pkgs.fetchurl {
      url = "https://files.pythonhosted.org/packages/14/50/0b608e2abee4fc695b4e7ff5f569f5d32faf84a49e322034716fa157d1cf/ctransformers-0.2.27-py3-none-any.whl";
      sha256 = "sha256-ajukdVZHGFDZX9vFkpmoKrkcnci0AgHF5+gtcTYHctk=";
    };
    propagatedBuildInputs = with py; [
      huggingface-hub
      py-cpuinfo
    ];
  };
in {
  devShells.default = pkgs.mkShell {
    name = "unnamed (1.0.0) devshell";
    NEO4J_HOME = "./.neo4j";
    NEO4J_CONF= "./.neo4j/conf";
    packages = (with py; [
      langchain-community
      setuptools
      langchain
      pydantic
      fastapi
      uvicorn
      python
      flake8
      typer
      neo4j
      wheel
      pip
    ]) ++ (with pkgs; [
      neo4j
    ]) ++ ([
      ctransformers
    ]);
    shellHook = ''
      neo4j start
      neo4j stop
      neo4j start
      trap "neo4j stop" EXIT INT TERM
    '';
  };
}