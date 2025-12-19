# So Much Is Broken Here (We Should Start a Refactor IMO) + Vibe Coding Warning

## Usage

### Enable Flakes

```nix
# ~/.config/nix/nix.conf
experimental-features = nix-command flakes
```

### Enable Caching (Optional)

```nix
# ~/.config/nix/nix.conf
substituters = https://cache.flox.dev https://cache.nixos.org
trusted-public-keys = flox-cache-public-1:7F4OyH7ZCnFhcze3fJdfyXYLQw/aV7GEed86nQ7IsOs= cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY=
```

### Restart Daemon

```bash
sudo systemctl restart nix-daemon
```

### Enter Nix Shell (At The Root Of This Repo)

```bash
nix develop . -L
```

### Populate Neo4j Database (With CLI)

```bash
python3 ./build.py --help
```

### Start API (Uses Port 8080, Hardcoded In ./lib./unnamed/agents.py)

```bash
unnamed # This is the correct command
```

### Curl Request

```bash
curl -X POST http://localhost:8080/ -H "Content-Type: application/json" -d '{"content": "Does ABCC11 impact microbe composition levels?", "persona": "researcher"}'
```
