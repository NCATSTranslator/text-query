{pkgs, lib, config, ...}:
let
  py = pkgs.python313Packages;
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
    doCheck = false;
  };
  python-for-mcps = pkgs.python313.withPackages (ps: [
    ps.fastmcp
    ps.httpx
    ps.neo4j
  ]);
  unnamed = py.buildPythonApplication rec {
    pname = "unnamed";
    version = "0.0.0";
    format = "pyproject";
    src = ../.;
    build-system = with py; [
      setuptools
      wheel
    ];
    propagatedBuildInputs = (with py; [
      langchain-community
      langchain-ollama
      langchain
      pydantic
      fastmcp
      fastapi
      uvicorn
      typer
      neo4j
    ]) ++ (with pkgs; [
      neo4j
    ]) ++ ([
      langchain-mcp-adapters
    ]);
    nativeBuildInputs = with pkgs; [
      makeWrapper
    ];
    makeWrapperArgs = [
      "--set PYTHON_INTERPRETER ${python-for-mcps}/bin/python3"
    ];
    doCheck = false;
  };
  python = pkgs.python313.withPackages (ps: [
    ps.flake8
    ps.orjson
    ps.neo4j
  ]);
in {
  devShells.default = pkgs.mkShell {
    name = "unnamed (1.0.0) devshell";
    NEO4J_HOME = "./.neo4j";
    NEO4J_CONF = "./.neo4j/conf";
    OLLAMA_MODELS = "./.ollama";
    packages = ([
      unnamed
      python
    ]) ++ (with pkgs; [
      neo4j
      ollama
    ]);
    shellHook = ''
      python3() {
        ${python}/bin/python3 "$@"
      }
      export -f python3

      if [ ! -d "./.neo4j/run/" ]; then
        neo4j start
        neo4j stop
      fi

      neo4j start

      ollama serve > /dev/null 2>&1 & OLLAMA_PID=$!
      for i in {1..30}; do
        if curl -s http://127.0.0.1:11434/api/tags > /dev/null 2>&1; then
          break
        fi
        sleep 1
      done

      ollama pull cogito:8b

      trap "neo4j stop && kill $OLLAMA_PID 2>/dev/null" EXIT INT TERM
    '';
  };
}