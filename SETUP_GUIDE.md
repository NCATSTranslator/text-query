# Getting Started with Claude Code (Vertex AI)

This guide walks you through installing and running Claude Code on your computer using our shared Vertex AI backend. No prior technical experience is required — just follow each step in order.

---

## What You Will Need

- A computer running **macOS**, **Windows**, or **Linux**
- An internet connection
- The **service account key file** (a `.json` file) provided to you by your admin

> **Keep your key file safe.** Treat it like a password — do not share it or post it online.

---

## Step 1: Open Your Terminal

A "terminal" is a text-based program on your computer where you type commands. You only need it for setup.

### macOS

1. Press **Cmd + Space** to open Spotlight Search
2. Type **Terminal** and press **Enter**

### Windows

1. Press the **Windows key** on your keyboard
2. Type **PowerShell**
3. Click **Windows PowerShell** (not the "ISE" version)

### Linux

1. Press **Ctrl + Alt + T** (works on most distributions)
2. Or search for **Terminal** in your application menu

> **Tip:** You can copy a command from this guide and paste it into your terminal. On macOS use **Cmd + V**, on Windows right-click in PowerShell, and on Linux use **Ctrl + Shift + V**.

---

## Step 2: Install Node.js

Claude Code requires Node.js (version 18 or newer). This is a one-time installation.

### macOS

Paste this command into your terminal and press **Enter**:

```
curl -fsSL https://fnm.vercel.app/install | bash
```

Close and reopen your terminal, then run:

```
fnm install 22
```

### Windows

1. Go to [https://nodejs.org](https://nodejs.org) in your web browser
2. Click the big green button labeled **LTS** to download the installer
3. Open the downloaded file and click **Next** through the installer, accepting all defaults
4. Close and reopen PowerShell when finished

### Linux

Paste this command into your terminal and press **Enter**:

```
curl -fsSL https://fnm.vercel.app/install | bash
```

Close and reopen your terminal, then run:

```
fnm install 22
```

### Verify It Worked

In your terminal, type:

```
node --version
```

You should see a version number like `v22.x.x`. If you see an error instead, try closing and reopening your terminal and running the command again.

---

## Step 3: Install Claude Code

In your terminal, run:

```
npm install -g @anthropic-ai/claude-code
```

This downloads and installs Claude Code. It may take a minute.

---

## Step 4: Save Your Key File

Your admin will give you a `.json` key file. You **must** save it to this exact location:

### macOS / Linux

Save or move the file to:

```
~/.config/claude-vertex/key.json
```

To create the folder and move the file, paste these commands (replace the path in the second command with wherever your browser downloaded the file):

```
mkdir -p ~/.config/claude-vertex
```

```
mv ~/Downloads/YOUR_KEY_FILE.json ~/.config/claude-vertex/key.json
```

### Windows

Save or move the file to:

```
C:\Users\YOUR_USERNAME\.config\claude-vertex\key.json
```

To create the folder and move the file, paste these commands into PowerShell (replace `YOUR_KEY_FILE.json` with the actual file name you downloaded):

```
New-Item -ItemType Directory -Force -Path "$HOME\.config\claude-vertex"
```

```
Move-Item "$HOME\Downloads\YOUR_KEY_FILE.json" "$HOME\.config\claude-vertex\key.json"
```

### Verify It Worked

- **macOS / Linux:** `cat ~/.config/claude-vertex/key.json` — you should see a block of text starting with `{`
- **Windows:** `Get-Content "$HOME\.config\claude-vertex\key.json"` — same thing

---

## Step 5: Configure Environment Variables

Claude Code needs to know how to connect to our Vertex AI backend. You do this by setting "environment variables" — small pieces of configuration that your terminal loads automatically.

Pick your platform below and follow the instructions. **Copy and paste each block exactly as shown — no changes needed.**

### macOS

Paste this into your terminal and press **Enter**:

```
cat >> ~/.zshrc << 'EOF'

# Claude Code — Vertex AI configuration
export CLAUDE_CODE_USE_VERTEX=1
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.config/claude-vertex/key.json"
export ANTHROPIC_VERTEX_PROJECT_ID="translator-microbiome"
export CLOUD_ML_REGION="us-east5"
EOF
```

Then reload your terminal configuration:

```
source ~/.zshrc
```

### Windows

Paste these commands into PowerShell **one at a time:**

```
[System.Environment]::SetEnvironmentVariable("CLAUDE_CODE_USE_VERTEX", "1", "User")
```

```
[System.Environment]::SetEnvironmentVariable("GOOGLE_APPLICATION_CREDENTIALS", "$($env:USERPROFILE)\.config\claude-vertex\key.json", "User")
```

```
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_VERTEX_PROJECT_ID", "translator-microbiome", "User")
```

```
[System.Environment]::SetEnvironmentVariable("CLOUD_ML_REGION", "us-east5", "User")
```

**Close and reopen PowerShell** for the changes to take effect.

### Linux

Paste this into your terminal and press **Enter**:

```
cat >> ~/.bashrc << 'EOF'

# Claude Code — Vertex AI configuration
export CLAUDE_CODE_USE_VERTEX=1
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.config/claude-vertex/key.json"
export ANTHROPIC_VERTEX_PROJECT_ID="translator-microbiome"
export CLOUD_ML_REGION="us-east5"
EOF
```

Then reload your terminal configuration:

```
source ~/.bashrc
```

### Verify It Worked

Close and reopen your terminal, then run:

- **macOS / Linux:** `echo $GOOGLE_APPLICATION_CREDENTIALS`
- **Windows:** `echo $env:GOOGLE_APPLICATION_CREDENTIALS`

You should see the path to your key file printed back. If it's blank, repeat Step 5.

---

## Step 6: Run Claude Code

In your terminal, type:

```
claude
```

Claude Code will start up. On first launch it will ask you to accept the terms of service — use your arrow keys and press Enter to accept.

You should now be in an interactive chat session with Claude. Try asking it something!

---

## Step 7: Set Up the Research Tools (Optional)

We have a set of custom research tools that extend Claude's capabilities. To install them, just paste the following message into your Claude Code session:

> Please clone the repository https://github.com/SMoxon/text-query.git into my home directory and install its dependencies. Walk me through anything that needs my input.

Claude will handle the rest — it will download the code, install dependencies, and configure everything. Just answer any questions it asks.

---

## Troubleshooting

### "command not found: claude"

Node.js or Claude Code didn't install correctly. Try:

```
npm install -g @anthropic-ai/claude-code
```

If that also fails, reinstall Node.js (Step 2).

### "Permission denied" or authentication errors

- Double-check that your key file is at `~/.config/claude-vertex/key.json` (Step 4)
- Make sure you closed and reopened your terminal after setting environment variables
- Verify with the check commands in Step 4 and Step 5

### "Could not find the key file"

- On macOS/Linux, run: `ls ~/.config/claude-vertex/key.json` — you should see the file listed
- On Windows, run: `Test-Path "$HOME\.config\claude-vertex\key.json"` — it should say `True`
- If the file isn't there, repeat Step 4

### Something else went wrong

Contact your admin with:
1. What step you were on
2. The exact error message (you can copy text from your terminal)
3. What platform you are using (macOS, Windows, or Linux)

---

## Quick Reference

Once everything is set up, all you need to do in the future is:

1. Open your terminal
2. Type `claude` and press Enter

That's it — you're ready to go.
