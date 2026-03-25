# Getting Started with text-query

## 1. Clone the repo

```bash
git clone https://github.com/TranslatorSRI/text-query.git
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
