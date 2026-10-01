# Cron Job Management

## Cron Job Structure

Each profile has a `cron/` directory with:
- `jobs.yaml` — Job definitions (name, schedule, deliver, skills, prompt file)
- `*.prompt` — Prompt templates with parameter substitution

## Creating Cron Jobs

### From Deployed Profile

```bash
# Admin jobs
hermes cronjob create \
  --prompt-file ~/.hermes/profiles/myadmin/cron/admin-hourly-pulse.prompt \
  --schedule "0 * * * *" \
  --deliver "telegram:5446665128" \
  --skills "hermes-agent-setup" \
  --name "Admin Hourly Pulse"

hermes cronjob create \
  --prompt-file ~/.hermes/profiles/myadmin/cron/admin-daily-report.prompt \
  --schedule "0 6 * * *" \
  --deliver "telegram:5446665128" \
  --skills "hermes-agent-setup" \
  --name "Admin Daily Report"

# Client jobs
hermes cronjob create \
  --prompt-file ~/.hermes/profiles/blessing/cron/client-daily-standup.prompt \
  --schedule "0 7 * * *" \
  --deliver "telegram:7200670846" \
  --skills "digital-assistant-workflow" \
  --name "Blessing Daily Standup"
```

### Direct Creation

```bash
hermes cronjob create \
  --prompt "Your prompt here" \
  --schedule "0 9 * * *" \
  --deliver "telegram:123456789" \
  --skills "skill-name" \
  --name "Job Name"
```

## Schedule Formats

| Format | Example | Meaning |
|--------|---------|---------|
| Cron | `0 7 * * *` | Daily 7:00 AM UTC |
| Cron | `0 */6 * * *` | Every 6 hours |
| Cron | `0 9 * * 1` | Monday 9:00 AM UTC |
| Cron | `0 8 1 * *` | 1st of month 8:00 AM UTC |
| Interval | `30m` | Every 30 minutes |
| Interval | `2h` | Every 2 hours |
| ISO | `2026-12-01T09:00:00` | One-time |

## Delivery Targets

| Target | Format | Use Case |
|--------|--------|----------|
| Specific DM | `telegram:123456789` | Direct message to user |
| Origin | `origin` | Same chat that created job |
| All channels | `all` | Broadcast to all connected |
| Local only | `local` | Save output, don't deliver |

## Managing Jobs

```bash
# List all jobs
hermes cronjob list

# Run on-demand
hermes cronjob run --job-id <id>

# Update job
hermes cronjob update --job-id <id> --schedule "0 8 * * *"

# Pause/Resume
hermes cronjob pause --job-id <id>
hermes cronjob resume --job-id <id>

# Remove
hermes cronjob remove --job-id <id>
```

## Job Output

- Saved to `~/.hermes/cron/output/<job_id>/<timestamp>.md`
- Delivered per `deliver` setting
- Check `last_status` and `last_delivery_error` in list output

## Best Practices

1. **Use skills** — Attach relevant skills for context
2. **Parameterize prompts** — Use `{{VARIABLES}}` in template, substitute on deploy
3. **Set appropriate schedules** — Hourly for pulses, daily for reports, weekly for reviews
4. **Monitor failures** — Check `last_status: "error"` in list output
5. **Clean up paused jobs** — Remove or resume stale jobs