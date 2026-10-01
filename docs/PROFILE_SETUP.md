# Profile Setup Guide

## Profile Types

### Admin Profile
- Full toolset (all 17 tools including `computer_use`, `delegation`, `terminal`, `code_execution`)
- Technical verbosity (`display.personality: technical`)
- Higher turn limit (`agent.max_turns: 50`)
- Destructive action confirmations enabled
- System monitoring cron jobs

### Client Profile
- Focused toolset (13 tools - no system-level tools)
- Concise display (`display.personality: concise`)
- Standard turn limit (`agent.max_turns: 30`)
- No destructive confirmations
- Productivity-focused cron jobs (standup, follow-ups, reviews)

## Creating a New Profile

### Using Deploy Script (Recommended)

```bash
# Admin
./scripts/deploy-profile.sh myadmin admin \
  --telegram-id 123456789 \
  --telegram-chats "123456789,-100987654321" \
  --home-channel 123456789

# Client
./scripts/deploy-profile.sh john client \
  --telegram-id 987654321 \
  --telegram-chats "987654321,-100987654321" \
  --home-channel 123456789 \
  --client-name "John" \
  --client-role "Marketing Manager" \
  --client-transition "AI-assisted content creation" \
  --client-priorities "Content automation, audience growth, revenue diversification"
```

### Manual Creation

1. Copy template:
   ```bash
   cp -r profiles/client-template ~/.hermes/profiles/newclient
   ```

2. Edit `config.yaml`:
   - Set `telegram.allowed_chats`
   - Set `TELEGRAM_HOME_CHANNEL`
   - Adjust toolsets if needed

3. Customize cron prompts in `cron/` with client-specific values

4. Add client memories to `memories/USER.md`

## Per-Profile Configuration

### Required Customizations

| Setting | Location | Admin | Client |
|---------|----------|-------|--------|
| `telegram.allowed_chats` | `config.yaml` | Admin DM + groups | Client DM + groups |
| `TELEGRAM_HOME_CHANNEL` | `config.yaml` | Admin user ID | Admin user ID |
| `TELEGRAM_ALLOWED_USERS` | Global `.env` | All user IDs | All user IDs |

### Optional Customizations

- `model.default` — Different model per profile
- `agent.max_turns` — Adjust for complexity
- `platform_toolsets.cli` — Add/remove tools
- `display.personality` — `concise` / `technical` / `verbose`

## Memories Structure

Each profile's `memories/` directory:

```
memories/
├── README.md
└── USER.md          # User profile (client profiles only)
```

### USER.md Template (Client Profiles)

```markdown
## User Profile — {{CLIENT_NAME}}
- Role: {{CLIENT_ROLE}} → {{CLIENT_TRANSITION}}
- Typical work: {{CLIENT_TYPICAL_WORK}}
- Biggest time sinks: {{CLIENT_TIME_SINKS}}
- Core needs: {{CLIENT_CORE_NEEDS}}
- Pain points: {{CLIENT_PAIN_POINTS}}

## Communication Preferences
- Format: {{CLIENT_FORMAT}}
- Tone: {{CLIENT_TONE}}
- Proactivity level: {{CLIENT_PROACTIVITY}}
- Uncertainty handling: {{CLIENT_UNCERTAINTY}}

## Boundaries (never without approval)
{{CLIENT_BOUNDARIES}}

## Current Priorities
{{CLIENT_PRIORITIES}}

## Working Style
{{CLIENT_WORKING_STYLE}}
```

## Skills Organization

```
skills/
├── README.md
├── skill-name/
│   ├── SKILL.md
│   ├── references/
│   ├── templates/
│   └── scripts/
```

Add skills via `skill_manage` tool or manually create `SKILL.md` files.

## Verification Checklist

After deploying a profile:

- [ ] Config exists: `~/.hermes/profiles/<name>/config.yaml`
- [ ] Telegram IDs in global `.env`: `TELEGRAM_ALLOWED_USERS=...`
- [ ] Profile starts: `hermes --profile <name>`
- [ ] Cron jobs created from `cron/jobs.yaml`
- [ ] Memories populated (especially `USER.md` for clients)
- [ ] Skills added as needed