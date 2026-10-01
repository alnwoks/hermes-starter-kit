# Telegram Routing — Single Bot, Multiple Profiles

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Single Telegram Bot                       │
│                    (One TELEGRAM_BOT_TOKEN)                  │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  Admin Profile │     │ Client: Blessing │   │ Client: John  │
│  (myadmin)    │     │ (blessing)       │     │ (john)        │
│               │     │                 │     │               │
│ allowed_chats:│     │ allowed_chats:  │     │ allowed_chats:│
│ "5446665128,  │     │ "7200670846,    │     │ "987654321,   │
│  -1004345112293"│  │  -1004345112293" │     │  -1004345112293"│
└───────────────┘     └───────────────┘     └───────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
        ┌─────────────────────────────────────────┐
        │     Global ~/.hermes/.env               │
        │  TELEGRAM_ALLOWED_USERS=5446665128,     │
        │    7200670846,987654321                 │
        └─────────────────────────────────────────┘
```

## Two Allowlist Systems (Critical)

### 1. Global DM Authorization — `.env` → `TELEGRAM_ALLOWED_USERS`
- **Controls**: Who can send DMs to the bot
- **Scope**: All profiles share this
- **Must include**: Every user ID across all profiles
- **Missing ID = blocked DMs** with "Blocked unauthorized user"

### 2. Group Observation — `config.yaml` → `telegram.allowed_chats`
- **Controls**: Which groups/channels the profile monitors and responds in
- **Scope**: Per-profile
- **Format**: Comma-separated chat IDs (negative for groups: `-100...`)
- **Does NOT affect DMs**

## Per-Profile Delivery

Cron jobs deliver to specific users via `deliver` field:

```yaml
# Admin jobs → Admin DM
deliver: "telegram:5446665128"

# Blessing jobs → Blessing DM  
deliver: "telegram:7200670846"

# John jobs → John DM
deliver: "telegram:987654321"
```

## Profile Switching in Telegram

When you message the bot, Hermes determines profile by:
1. **Chat ID** → Matches `telegram.allowed_chats` in profile config
2. **User ID** → Matches `TELEGRAM_ALLOWED_USERS` in `.env`

For DMs: Each profile can be addressed by starting a conversation from that user's account.

For Groups: Add the bot to groups, add group ID to relevant profile's `allowed_chats`.

## Setup Checklist

### Global (Once)
- [ ] Create bot via @BotFather → get `TELEGRAM_BOT_TOKEN`
- [ ] Add to `~/.hermes/.env`: `TELEGRAM_BOT_TOKEN=...`
- [ ] Add ALL user IDs to `TELEGRAM_ALLOWED_USERS` (comma-separated)

### Per Admin Profile
- [ ] `config.yaml`: `telegram.allowed_chats` = admin DM + monitored groups
- [ ] `config.yaml`: `TELEGRAM_HOME_CHANNEL` = admin user ID
- [ ] Cron jobs: `deliver: "telegram:<admin_id>"`

### Per Client Profile
- [ ] `config.yaml`: `telegram.allowed_chats` = client DM + monitored groups
- [ ] `config.yaml`: `TELEGRAM_HOME_CHANNEL` = admin user ID (for notifications)
- [ ] Cron jobs: `deliver: "telegram:<client_id>"`
- [ ] Add client ID to global `TELEGRAM_ALLOWED_USERS`

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Blocked unauthorized user" | User ID missing from `TELEGRAM_ALLOWED_USERS` | Add to global `.env` |
| Bot doesn't respond in group | Group ID not in profile's `allowed_chats` | Add `-100...` to `config.yaml` |
| Cron job not delivered | Wrong `deliver` target | Use `telegram:<correct_user_id>` |
| Admin gets client messages | Profile mismatch | Check `allowed_chats` per profile |

## Testing

```bash
# Test admin profile
hermes --profile myadmin
# Send DM from admin account → should respond as admin

# Test client profile  
hermes --profile blessing
# Send DM from Blessing's account → should respond as Blessing

# Test cron delivery
hermes cronjob run --job-id <blessing_standup_job_id>
# Should appear in Blessing's DM
```