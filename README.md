# Hermes Agent Starter Kit

A portable, git-trackable template system for deploying Hermes Agent profiles (admin + clients) with full configuration, cron jobs, skills, and memories.

## Structure

```
hermes-starter-kit/
├── profiles/
│   ├── admin/
│   │   ├── config.yaml              # Admin profile template
│   │   ├── cron/
│   │   │   ├── jobs.yaml            # Cron job definitions
│   │   │   ├── admin-hourly-pulse.prompt
│   │   │   ├── admin-daily-report.prompt
│   │   │   ├── admin-health-check.prompt
│   │   │   └── admin-weekly-deepdive.prompt
│   │   ├── skills/                  # Add admin skills here
│   │   └── memories/                # Add admin memories here
│   └── client-template/
│       ├── config.yaml              # Client profile template (parameterized)
│       ├── cron/
│       │   ├── jobs.yaml
│       │   ├── client-daily-standup.prompt
│       │   ├── client-followup-check.prompt
│       │   ├── client-weekly-review.prompt
│       │   └── client-monthly-goals.prompt
│       ├── skills/                  # Add client skills here
│       └── memories/                # Add client memories here
├── scripts/
│   ├── deploy-profile.sh            # Bash deployment script
│   ├── deploy_profile.py            # Python deployment script (cross-platform)
│   ├── export-system.py             # Export live system to starter kit
│   └── migrate-system.py            # Migrate system to new machine
├── docs/
│   ├── PROFILE_SETUP.md             # Profile configuration guide
│   ├── CRON_JOBS.md                 # Cron job management
│   ├── TELEGRAM_ROUTING.md          # Chat-based routing with single bot
│   └── GIT_WORKFLOW.md              # Git tracking best practices
└── README.md                        # This file
```

## Quick Start

### 1. Clone & Deploy Admin Profile

```bash
git clone <your-repo> hermes-starter-kit
cd hermes-starter-kit

# Deploy admin profile (you)
./scripts/deploy-profile.sh myadmin admin \
  --telegram-id 5446665128 \
  --telegram-chats "5446665128,-1004345112293" \
  --home-channel 5446665128
```

### 2. Deploy Client Profile

```bash
# Deploy client profile (e.g., Blessing)
./scripts/deploy-profile.sh blessing client \
  --telegram-id 7200670846 \
  --telegram-chats "7200670846,-1004345112293" \
  --home-channel 5446665128 \
  --client-name "Blessing" \
  --client-role "Customer Success & Operations" \
  --client-transition "Automation/AI workflow solutions" \
  --client-priorities "Building automation/AI skills, growing professional presence, finding income opportunities, creating productivity systems"
```

### 3. Start Profiles

```bash
# Admin session
hermes --profile myadmin

# Client session
hermes --profile blessing
```

### 4. Create Cron Jobs

```bash
# From the deployed profile's cron/jobs.yaml, create each job:
hermes cronjob create \
  --prompt-file ~/.hermes/profiles/blessing/cron/client-daily-standup.prompt \
  --schedule "0 7 * * *" \
  --deliver "telegram:7200670846" \
  --skills "digital-assistant-workflow" \
  --name "Blessing Daily Standup"
```

## Key Features

### Parameterized Templates
- `{{ADMIN_TELEGRAM_ID}}`, `{{CLIENT_TELEGRAM_ID}}` — User IDs
- `{{CLIENT_NAME}}`, `{{CLIENT_ROLE}}`, `{{CLIENT_TRANSITION}}`, `{{CLIENT_PRIORITIES}}` — Client context
- `telegram.allowed_chats`, `TELEGRAM_HOME_CHANNEL` — Per-profile Telegram config

### Single Bot, Multi-Profile Routing
- One Telegram bot token shared across all profiles
- `TELEGRAM_ALLOWED_USERS` in global `~/.hermes/.env` contains ALL user IDs
- Per-profile `config.yaml` has `telegram.allowed_chats` for group monitoring
- Cron jobs deliver to specific user IDs via `deliver: "telegram:<id>"`

### Git-Trackable
- All configs, prompts, skills in plain text
- No secrets in repo (API keys via `.env` / env vars)
- Deploy scripts recreate exact profiles on any machine

### Portable Migration
```bash
# Export current live system to starter kit
python3 scripts/export-system.py --output hermes-starter-kit

# On new machine: deploy from starter kit
python3 scripts/deploy_profile.py blessing client --telegram-id 7200670846 ...
```

## Required Environment

Global `~/.hermes/.env`:
```bash
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_ALLOWED_USERS=5446665128,7200670846,<other_client_ids>
OPENROUTER_API_KEY=sk-or-...
```

Per-profile configs handle the rest.

## Adding New Clients

1. Run deploy script with client-specific parameters
2. Add their Telegram ID to global `TELEGRAM_ALLOWED_USERS`
3. Customize their `memories/` with USER.md (profile, preferences, boundaries)
4. Add client-specific skills to `skills/`
5. Adjust cron schedules in `cron/jobs.yaml` as needed

## Updating Profiles

1. Edit templates in `hermes-starter-kit/profiles/`
2. Commit to git
3. Re-deploy on target machines (scripts are idempotent)
4. Or manually sync changes to `~/.hermes/profiles/<name>/`

## Files to Gitignore

```
# Never commit these
.env
*.key
*.pem
auth.json
gateway_state.json
gateway.pid
logs/
state.db
profiles/*/memories/USER.md  # Contains personal info
```

## Documentation

- [Profile Setup](docs/PROFILE_SETUP.md)
- [Cron Jobs](docs/CRON_JOBS.md)
- [Telegram Routing](docs/TELEGRAM_ROUTING.md)
- [Git Workflow](docs/GIT_WORKFLOW.md)