# Git Workflow for Hermes Starter Kit

## Repository Structure

```
hermes-starter-kit/
├── .gitignore
├── README.md
├── profiles/
│   ├── admin/
│   │   ├── config.yaml
│   │   ├── cron/
│   │   │   ├── jobs.yaml
│   │   │   └── *.prompt
│   │   ├── skills/
│   │   │   └── README.md
│   │   └── memories/
│   │       └── README.md
│   └── client-template/
│       ├── config.yaml
│       ├── cron/
│       │   ├── jobs.yaml
│       │   └── *.prompt
│       ├── skills/
│       │   └── README.md
│       └── memories/
│           └── README.md
├── scripts/
│   ├── deploy-profile.sh
│   ├── deploy_profile.py
│   ├── export-system.py
│   └── migrate-system.py
└── docs/
    ├── PROFILE_SETUP.md
    ├── CRON_JOBS.md
    ├── TELEGRAM_ROUTING.md
    └── GIT_WORKFLOW.md
```

## .gitignore

```gitignore
# Secrets - NEVER commit
.env
*.key
*.pem
auth.json
*.secret

# Runtime state
gateway_state.json
gateway.pid
gateway.lock
logs/
state.db
*.pid

# Per-profile secrets (deployed, not in kit)
profiles/*/.env
profiles/*/memories/USER.md

# Python
__pycache__/
*.pyc
*.pyo
.pytest_cache/

# OS
.DS_Store
Thumbs.db
```

## What to Track in Git

### ✅ Track These
- All profile templates (`profiles/*/config.yaml`)
- Cron job definitions (`profiles/*/cron/jobs.yaml`, `*.prompt`)
- Deployment scripts (`scripts/*.sh`, `scripts/*.py`)
- Documentation (`docs/*.md`, `README.md`)
- Skill templates (if any in `profiles/*/skills/`)

### ❌ Never Track These
- API keys, tokens, secrets
- Runtime state (gateway, database, logs)
- Personal memories (`USER.md` with real user data)
- Per-machine `.env` files

## Branching Strategy

```
main                    # Stable templates, production-ready
├── feature/new-client  # Adding new client profile template
├── feature/new-skill   # Adding reusable skill template
├── fix/config-bug      # Fixing template issues
└── experiment/...      # Experimental changes
```

## Commit Conventions

```
type(scope): description

Types:
  feat    - New template, script, or feature
  fix     - Bug fix in template/script
  docs    - Documentation only
  refactor- Code restructuring
  chore   - Maintenance (deps, tooling)

Examples:
  feat(client): add monthly goal check cron template
  fix(admin): correct telegram allowed_chats default
  docs: add telegram routing guide
  refactor(scripts): unify deploy scripts
```

## Deployment Workflow

### 1. Local Development

```bash
# Edit templates in hermes-starter-kit/
vim profiles/client-template/config.yaml

# Test deploy locally
./scripts/deploy-profile.sh testclient client --telegram-id 111222333 --dry-run

# Verify generated config
cat ~/.hermes/profiles/testclient/config.yaml
```

### 2. Commit & Push

```bash
git add profiles/client-template/config.yaml
git commit -m "feat(client): update default model for client profiles"
git push origin main
```

### 3. Deploy to Target Machine

```bash
# On target machine
git clone <repo> hermes-starter-kit
cd hermes-starter-kit

# Deploy profiles
python3 scripts/deploy_profile.py myadmin admin --telegram-id 5446665128 ...
python3 scripts/deploy_profile.py blessing client --telegram-id 7200670846 ...

# Set up global env
cp profiles/client-template/.env.template ~/.hermes/.env
# Edit ~/.hermes/.env with real keys
```

### 4. Sync Updates

```bash
# On target machine
cd hermes-starter-kit
git pull origin main

# Re-deploy (scripts are idempotent)
python3 scripts/deploy_profile.py blessing client --telegram-id 7200670846 ...

# Re-create cron jobs if prompts changed
hermes cronjob create --prompt-file ~/.hermes/profiles/blessing/cron/client-daily-standup.prompt ...
```

## Exporting Live System to Kit

```bash
# Capture current live profiles to starter kit
python3 scripts/export-system.py --output hermes-starter-kit --profiles admin blessing --include-global

# Review changes
cd hermes-starter-kit
git diff

# Commit updates
git add -A
git commit -m "feat: sync live system configs to starter kit"
git push
```

## Secrets Management

### Development
- Use `.env.local` (gitignored) for local testing
- Never hardcode keys in templates — use `«redacted»` placeholders

### Production
- Store secrets in environment variables or secret manager
- `OPENROUTER_API_KEY` → env var
- `TELEGRAM_BOT_TOKEN` → env var
- `TELEGRAM_ALLOWED_USERS` → env var (comma-separated)

### Template Pattern
```yaml
# In config.yaml templates
openrouter:
  api_key: «redacted:sk-…»  # Set via env: OPENROUTER_API_KEY
```

## CI/CD (Optional)

```yaml
# .github/workflows/validate.yml
name: Validate Templates
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate YAML syntax
        run: |
          python3 -c "
import yaml, sys
for f in sys.argv[1:]:
    with open(f) as fp:
        yaml.safe_load(fp)
    print(f'OK: {f}')
" $(find profiles -name "*.yaml")
      - name: Test deploy scripts (dry-run)
        run: |
          python3 scripts/deploy_profile.py testadmin admin --telegram-id 111 --dry-run
          python3 scripts/deploy_profile.py testclient client --telegram-id 222 --dry-run
```

## Migration Checklist

When moving to new machine:

- [ ] Clone starter kit repo
- [ ] Run `python3 scripts/migrate-system.py --kit . --setup-env`
- [ ] Deploy each profile: `python3 scripts/deploy_profile.py ...`
- [ ] Edit `~/.hermes/.env` with real API keys
- [ ] Add all user IDs to `TELEGRAM_ALLOWED_USERS`
- [ ] Create cron jobs from `cron/jobs.yaml`
- [ ] Verify: `hermes --profile <name>` for each
- [ ] Test cron: `hermes cronjob run --job-id <id>`