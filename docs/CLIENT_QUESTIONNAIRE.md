# Client Questionnaire — Setup Guide

This directory holds client configuration files. Each file is a completed questionnaire that feeds into `scripts/generate.py`.

## Workflow

### 1. Fill Questionnaire (`clients/<name>.yaml`)

The questionnaire maps to these sections:

| Section | Purpose | Used By |
|---------|---------|---------|
| `profile_name` / `profile_type` | Directory and type | Deploy script |
| `telegram_id` / `telegram_chats` | Routing and authorization | Config template |
| `home_channel` | Admin notification ID | Config template |
| `client_name` / `client_role` / `client_transition` | Profile context | Memory (USER.md) |
| `client_priorities` | Daily standup content | Cron prompts |
| `daily_work` / `time_sinks` | Profile understanding | Memory + skills |
| `transition_goal` / `blockers` | Strategic context | Memory + weekly reviews |
| `format_pref` / `tone_pref` | Communication style | Config (display) |
| `proactivity` / `uncertainty_pref` | Behavior tuning | Memory |
| `boundaries` | Guardrails | Memory (guardrails) |
| `priorities_list` | Standup briefings | Cron prompts |

### 2. Generate / Deploy

```bash
python3 scripts/generate.py --client clients/blessing.yaml --env production
```

This creates:
- `~/.hermes/profiles/blessing/config.yaml` (from template + questionnaire)
- `~/.hermes/profiles/blessing/memories/USER.md` (from questionnaire)
- Profile is ready to use: `hermes --profile blessing`

### 3. Create Cron Jobs

After deployment, create the client's recurring jobs:

```bash
# From starter kit templates (substitute client-specific values)
hermes cronjob create \
  --prompt-file ~/.hermes/profiles/blessing/cron/client-daily-standup.prompt \
  --schedule "0 7 * * *" \
  --deliver "telegram:7200670846" \
  --skills "digital-assistant-workflow"

# Repeat for follow-up check, weekly review, monthly goals
```

### 4. Add Client-Specific Skills (Optional)

If the client has unique workflows:

```bash
mkdir -p ~/.hermes/profiles/blessing/skills/my-workflow/
# Create SKILL.md, references/, templates/
```

### 5. Commit Questionnaire (Not Secrets)

The questionnaire file (`clients/blessing.yaml`) contains **no secrets** (only Telegram IDs and preferences). It can be safely committed:

```bash
git add clients/blessing.yaml
git commit -m "feat(client): add Blessing setup questionnaire"
```

The **deployed config** (with full Telegram routing) and **memory profile** are generated locally and should not be committed (they contain runtime state).

## Template Variables in Prompts

The questionnaire variables are substituted into prompt templates:
- `{{CLIENT_TELEGRAM_ID}}`
- `{{CLIENT_NAME}}`
- `{{CLIENT_ROLE}}`
- `{{CLIENT_TRANSITION}}`
- `{{CLIENT_PRIORITIES}}`

These substitutions happen automatically when prompts are processed, or manually if needed.
