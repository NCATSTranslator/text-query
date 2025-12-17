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
  langchain-mcp-adapters = py.buildPythonPackage rec {
    pname = "langchain-mcp-adapters";
    version = "0.2.1";
    format = "pyproject";
    src = pkgs.fetchurl {
      url = "https://files.pythonhosted.org/packages/d9/52/cebf0ef5b1acef6cbc63d671171d43af70f12d19f55577909c7afa79fb6e/langchain_mcp_adapters-0.2.1.tar.gz";
      sha256 = "sha256-WOZMROjfKcp+s7ZWz4yZMe9kOGU018omGYLjvcY/MXY=";
    };
    nativeBuildInputs = with py; [
      pdm-backend
    ];
    propagatedBuildInputs = with py; [
      typing-extensions
      langchain-core
      mcp
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
      langchain-mcp-adapters
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