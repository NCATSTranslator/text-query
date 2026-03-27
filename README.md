# Getting Started with text-query

## 0. Prerequisite: Install Claude Code (you can use other agents, but this recipe uses Claude Code)

1. Follow instructions here (just step 1): https://code.claude.com/docs/en/quickstart
2. If you have your own Anthropic account (encouraged) follow the login instructions in step 2 and 3 and skip to step 6 in this recipe. 

## 1. Clone the repo

```bash
git clone https://github.com/NCATSTranslator/text-query
cd text-query
```

## 2. Copy the environment template

```bash
cp .env-example .env
```

## 3. Download your GCP service account key

1. Get a key from Sierra Moxon. 

```bash
mv ~/Downloads/translator-microbiome-*.json ~/.config/gcloud/translator-microbiome-key.json
```

## 4. Update `.env` with your key path and project ID

Open `.env` and replace the placeholder values:

```bash
export CLAUDE_CODE_USE_VERTEX=1
export CLOUD_ML_REGION=us-east5
export ANTHROPIC_VERTEX_PROJECT_ID=translator-microbiome
export GOOGLE_CLOUD_PROJECT=translator-microbiome
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/translator-microbiome-key.json
```

Replace `/path/to/your/translator-microbiome-key.json` with the actual path from step 3. For example:

## 5. Source the environment and run Claude Code

```bash
source .env
claude
```

Claude Code will now use Vertex AI with the `translator-microbiome` project.
Claude Code will read the skills in this cloned project, and have access immediately to some command line skills that we provide, including `translator-query` 

## 6. In your launched Claude Code session from above

```
source_data % claude                                       
▗ ▗   ▖ ▖  Claude Code v2.1.85
           Opus 4.6 (1M context) · Claude Max
  ▘▘ ▝▝    ~/Documents/source_data

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
❯  /translator-query How Are Microbiome Communities in the Skin Affected by Changes in ABCC11? 
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  ? for shortcuts                            

