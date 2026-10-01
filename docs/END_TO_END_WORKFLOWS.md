# End-to-End Workflows Documentation

This guide covers all 4 tracks from questionnaire to live deployment.

---

## Track 1: Fix `generate.py` (Separate Deploy from Generate)

### Problem
Current `generate.py` runs `subprocess.run(deploy_profile.py)` which fails in proot environments.

### Fix Applied
Changed `KIT_DIR = Path("hermes-starter-kit")` → `KIT_DIR = Path(__file__).parent.parent`

### Recommended Enhancement
Split into two commands:
```bash
# Step 1: Generate artifacts (no subprocess)
python3 scripts/generate.py --client clients/blessing.yaml --generate-only

# Step 2: Deploy (uses deploy_profile.py directly)
python3 scripts/deploy_profile.py blessing client --telegram-id 7200670846 ...
```

### Implementation (in `generate.py`)
```python
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--client", required=True)
    parser.add_argument("--env", default="production")
    parser.add_argument("--generate-only", action="store_true",
                        help="Only generate config/memories, skip deploy")
    parser.add_argument("--deploy-only", action="store_true",
                        help="Only run deploy_profile.py, skip generation")
    args = parser.parse_args()

    if not args.deploy_only:
        generate_artifacts(args.client)
    if not args.generate_only:
        run_deploy(args.client)
```

---

## Track 2: Build Deployment Repo (Option 4)

### Structure
```
my-deployment-repo/
├── .github/workflows/deploy.yml    # CI/CD
├── hermes-starter-kit/             # Git submodule (this repo)
├── clients/
│   ├── blessing.yaml               # Questionnaire (committed)
│   ├── john.yaml
│   └── template.yaml
├── environments/
│   ├── production/
│   │   ├── admin.yaml
│   │   └── .env.template           # Not committed
│   └── staging/
│       └── ...
├── deploy.sh                       # Local one-command deploy
└── README.md
```

### Setup
```bash
# In your deployment repo
git submodule add git@github.com:alnwoks/hermes-starter-kit.git hermes-starter-kit
git commit -m "feat: add hermes starter kit as submodule"

# Create client configs from template
cp hermes-starter-kit/clients/template.yaml clients/blessing.yaml
# Edit blessing.yaml with client details
```

### Local Deploy Script (`deploy.sh`)
```bash
#!/bin/bash
set -euo pipefail

ENV=${1:-production}
echo "=== Deploying to $ENV ==="

# Update submodule
git submodule update --init --recursive

# Load environment
source environments/$ENV/.env 2>/dev/null || echo "No .env for $ENV"

# Deploy admin
python3 hermes-starter-kit/scripts/generate.py \
  --client environments/$ENV/admin.yaml \
  --env $ENV --deploy-only

# Deploy all clients
for client_file in clients/*.yaml; do
  [[ -f "$client_file" ]] || continue
  python3 hermes-starter-kit/scripts/generate.py \
    --client "$client_file" \
    --env $ENV
done

echo "=== Deployment Complete ==="
```

### CI/CD (`.github/workflows/deploy.yml`)
```yaml
name: Deploy Hermes
on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive
      
      - name: Setup SSH
        run: |
          echo "${{ secrets.SSH_KEY }}" > ~/.ssh/id_ed25519
          chmod 600 ~/.ssh/id_ed25519
          ssh-keyscan github.com >> ~/.ssh/known_hosts
      
      - name: Deploy
        env:
          ADMIN_TELEGRAM_ID: ${{ secrets.ADMIN_TELEGRAM_ID }}
        run: |
          source environments/production/.env
          ./deploy.sh production
```

---

## Track 3: Test Deployed Profile

### Verify Config
```bash
cat ~/.hermes/profiles/blessing/config.yaml
# Check: telegram.allowed_chats = "7200670846,-1004345112293"
# Check: TELEGRAM_HOME_CHANNEL = 5446665128
# Check: toolset = focused (no computer_use, delegation, terminal)
```

### Verify Memory
```bash
cat ~/.hermes/profiles/blessing/memories/USER.md
# Check: Role, transition, priorities, boundaries, daily work, blockers
```

### Verify Cron Prompts
```bash
cat ~/.hermes/profiles/blessing/cron/client-daily-standup.prompt
# Check: Client name, role, transition, priorities substituted
```

### Test Profile Session
```bash
# Start client profile
hermes --profile blessing

# In session, test:
# "Give me my daily standup" → should use parameterized prompt
# "What are my priorities?" → should reference USER.md memory
```

### Create Cron Jobs
```bash
# Using Hermes binary directly (adjust subcommand for your build)
/opt/hermes-agent/bin/hermes cron create \
  --prompt-file ~/.hermes/profiles/blessing/cron/client-daily-standup.prompt \
  --schedule "0 7 * * *" \
  --deliver "telegram:7200670846" \
  --skills "digital-assistant-workflow" \
  --name "Blessing Daily Standup"

# Repeat for: followup-check, weekly-review, monthly-goals
```

---

## Track 4: Commit & Push to GitHub

### Files to Commit
```
✅ clients/blessing.yaml          # Questionnaire (no secrets)
✅ clients/template.yaml          # Template
✅ environments/production/admin.yaml
✅ scripts/generate.py            # Fixed KIT_DIR
✅ docs/CLIENT_QUESTIONNAIRE.md
✅ README.md                      # Updated with workflow docs
```

### Files NOT to Commit (in .gitignore)
```
.env                              # Secrets
profiles/*/memories/USER.md       # Generated personal data
profiles/*/config.yaml            # Generated (runtime)
*.key, *.pem, auth.json           # Credentials
```

### Push Commands
```bash
cd /root/hermes-starter-kit

# Stage changes
git add clients/blessing.yaml clients/template.yaml \
  environments/production/admin.yaml \
  scripts/generate.py docs/CLIENT_QUESTIONNAIRE.md README.md

# Commit
git commit -m "docs: add end-to-end workflow docs for all 4 tracks"

# Push with SSH
GIT_SSH_COMMAND="ssh -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no" \
  git push origin master
```

### Verify on GitHub
1. Go to: https://github.com/alnwoks/hermes-starter-kit
2. Check: `clients/`, `environments/`, `scripts/generate.py`, `docs/`
3. Verify `README.md` has new "Client Questionnaire → Deploy Workflow" section

---

## Complete Workflow Summary

| Track | Input | Output | Command |
|-------|-------|--------|---------|
| 1. Fix | `generate.py` with hardcoded path | Fixed `KIT_DIR` | `git commit -m "fix: KIT_DIR resolution"` |
| 2. Deploy Repo | `clients/*.yaml` + submodule | Deployed profiles + cron | `./deploy.sh production` |
| 3. Test | Deployed profile | Live session + cron jobs | `hermes --profile blessing` |
| 4. Push | All docs + fixes | GitHub updated | `git push` |

---

## Quick Reference

```bash
# 1. Fix generate.py (already done)
# 2. Create deployment repo
git submodule add git@github.com:alnwoks/hermes-starter-kit.git
# 3. Test locally
python3 hermes-starter-kit/scripts/generate.py --client clients/blessing.yaml
# 4. Push
GIT_SSH_COMMAND="ssh -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no" git push
```