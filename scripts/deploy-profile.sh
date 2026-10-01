#!/bin/bash
# deploy-profile.sh — Deploy a Hermes Agent profile from starter kit
# Usage: ./deploy-profile.sh <profile-name> <profile-type> [options]
#   profile-name: e.g., "blessing", "john", "sarah"
#   profile-type: "admin" or "client"
# Options:
#   --telegram-id <id>       Client/admin Telegram user ID
#   --telegram-chats <ids>   Comma-separated chat IDs for allowed_chats
#   --home-channel <id>      TELEGRAM_HOME_CHANNEL (admin user ID)
#   --openrouter-key <key>   OpenRouter API key (or set OPENROUTER_API_KEY env)
#   --dry-run                Show what would be done without executing

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KIT_DIR="$(dirname "$SCRIPT_DIR")"
HERMES_DIR="${HOME}/.hermes"

PROFILE_NAME=""
PROFILE_TYPE=""
TELEGRAM_ID=""
TELEGRAM_CHATS=""
HOME_CHANNEL=""
OPENROUTER_KEY=""
DRY_RUN=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --telegram-id) TELEGRAM_ID="$2"; shift 2 ;;
        --telegram-chats) TELEGRAM_CHATS="$2"; shift 2 ;;
        --home-channel) HOME_CHANNEL="$2"; shift 2 ;;
        --openrouter-key) OPENROUTER_KEY="$2"; shift 2 ;;
        --dry-run) DRY_RUN=true; shift ;;
        *)
            if [[ -z "$PROFILE_NAME" ]]; then
                PROFILE_NAME="$1"
            elif [[ -z "$PROFILE_TYPE" ]]; then
                PROFILE_TYPE="$1"
            else
                echo "Unknown argument: $1" >&2
                exit 1
            fi
            shift
            ;;
    esac
done

if [[ -z "$PROFILE_NAME" || -z "$PROFILE_TYPE" ]]; then
    echo "Usage: $0 <profile-name> <admin|client> [options]" >&2
    echo "Options:" >&2
    echo "  --telegram-id <id>       User Telegram ID" >&2
    echo "  --telegram-chats <ids>   Comma-separated allowed chat IDs" >&2
    echo "  --home-channel <id>      TELEGRAM_HOME_CHANNEL (admin ID)" >&2
    echo "  --openrouter-key <key>   OpenRouter API key" >&2
    echo "  --dry-run                Show what would be done" >&2
    exit 1
fi

if [[ "$PROFILE_TYPE" != "admin" && "$PROFILE_TYPE" != "client" ]]; then
    echo "Profile type must be 'admin' or 'client'" >&2
    exit 1
fi

TARGET_DIR="${HERMES_DIR}/profiles/${PROFILE_NAME}"
TEMPLATE_DIR="${KIT_DIR}/profiles/${PROFILE_TYPE}-template"

if [[ ! -d "$TEMPLATE_DIR" ]]; then
    echo "Template not found: $TEMPLATE_DIR" >&2
    exit 1
fi

echo "=== Deploying $PROFILE_TYPE profile: $PROFILE_NAME ==="
echo "Source: $TEMPLATE_DIR"
echo "Target: $TARGET_DIR"

# Create target directory
if [[ "$DRY_RUN" == "true" ]]; then
    echo "[DRY RUN] Would create: $TARGET_DIR/{skills,cron,memories}"
else
    mkdir -p "$TARGET_DIR"/{skills,cron,memories}
fi

# Process config.yaml with substitutions
CONFIG_SRC="${TEMPLATE_DIR}/config.yaml"
CONFIG_DST="${TARGET_DIR}/config.yaml"

if [[ "$DRY_RUN" == "true" ]]; then
    echo "[DRY RUN] Would process config.yaml with substitutions:"
    echo "  {{ADMIN_TELEGRAM_ID}} -> ${ADMIN_TELEGRAM_ID:-<not set>}"
    echo "  {{CLIENT_TELEGRAM_ID}} -> ${CLIENT_TELEGRAM_ID:-<not set>}"
    echo "  {{CLIENT_NAME}} -> ${CLIENT_NAME:-<not set>}"
    echo "  {{CLIENT_ROLE}} -> ${CLIENT_ROLE:-<not set>}"
    echo "  {{CLIENT_TRANSITION}} -> ${CLIENT_TRANSITION:-<not set>}"
    echo "  {{CLIENT_PRIORITIES}} -> ${CLIENT_PRIORITIES:-<not set>}"
    echo "  telegram.allowed_chats -> ${TELEGRAM_CHATS:-<empty>}"
    echo "  TELEGRAM_HOME_CHANNEL -> ${HOME_CHANNEL:-<empty>}"
else
    # Determine substitution values
    if [[ "$PROFILE_TYPE" == "admin" ]]; then
        ADMIN_TELEGRAM_ID="${TELEGRAM_ID:-${HOME_CHANNEL:-}}"
        sed -e "s/{{ADMIN_TELEGRAM_ID}}/${ADMIN_TELEGRAM_ID}/g" \
            -e "s|telegram:\\n  allowed_chats: \"\"|telegram:\\n  allowed_chats: \"${TELEGRAM_CHATS}\"|" \
            -e "s|TELEGRAM_HOME_CHANNEL: \"\"|TELEGRAM_HOME_CHANNEL: ${HOME_CHANNEL:-$ADMIN_TELEGRAM_ID}|" \
            "$CONFIG_SRC" > "$CONFIG_DST"
    else
        CLIENT_TELEGRAM_ID="${TELEGRAM_ID:-}"
        CLIENT_NAME="${CLIENT_NAME:-$PROFILE_NAME}"
        CLIENT_ROLE="${CLIENT_ROLE:-Client}"
        CLIENT_TRANSITION="${CLIENT_TRANSITION:-Automation/AI transition}"
        CLIENT_PRIORITIES="${CLIENT_PRIORITIES:-Automation skills, professional growth, productivity systems}"
        sed -e "s/{{CLIENT_TELEGRAM_ID}}/${CLIENT_TELEGRAM_ID}/g" \
            -e "s/{{CLIENT_NAME}}/${CLIENT_NAME}/g" \
            -e "s/{{CLIENT_ROLE}}/${CLIENT_ROLE}/g" \
            -e "s/{{CLIENT_TRANSITION}}/${CLIENT_TRANSITION}/g" \
            -e "s/{{CLIENT_PRIORITIES}}/${CLIENT_PRIORITIES}/g" \
            -e "s|telegram:\\n  allowed_chats: \"\"|telegram:\\n  allowed_chats: \"${TELEGRAM_CHATS}\"|" \
            -e "s|TELEGRAM_HOME_CHANNEL: \"\"|TELEGRAM_HOME_CHANNEL: ${HOME_CHANNEL:-}|" \
            "$CONFIG_SRC" > "$CONFIG_DST"
    fi
    echo "Config written: $CONFIG_DST"
fi

# Copy cron jobs (process prompt files)
CRON_SRC_DIR="${TEMPLATE_DIR}/cron"
CRON_DST_DIR="${TARGET_DIR}/cron"

if [[ "$DRY_RUN" == "true" ]]; then
    echo "[DRY RUN] Would copy cron jobs from $CRON_SRC_DIR to $CRON_DST_DIR"
else
    cp -r "$CRON_SRC_DIR"/* "$CRON_DST_DIR"/
    # Process prompt files for client profiles
    if [[ "$PROFILE_TYPE" == "client" ]]; then
        for prompt in "$CRON_DST_DIR"/*.prompt; do
            [[ -f "$prompt" ]] || continue
            sed -i \
                -e "s/{{CLIENT_TELEGRAM_ID}}/${CLIENT_TELEGRAM_ID}/g" \
                -e "s/{{CLIENT_NAME}}/${CLIENT_NAME}/g" \
                -e "s/{{CLIENT_ROLE}}/${CLIENT_ROLE}/g" \
                -e "s/{{CLIENT_TRANSITION}}/${CLIENT_TRANSITION}/g" \
                -e "s/{{CLIENT_PRIORITIES}}/${CLIENT_PRIORITIES}/g" \
                "$prompt"
        done
    fi
    echo "Cron jobs copied to: $CRON_DST_DIR"
fi

# Create skills README
if [[ "$DRY_RUN" == "true" ]]; then
    echo "[DRY RUN] Would create skills/README.md"
else
    cat > "${TARGET_DIR}/skills/README.md" <<EOF
# ${PROFILE_NAME^} Skills

Add custom skills here. Each skill should have:
- SKILL.md (definition)
- references/ (optional)
- templates/ (optional)
- scripts/ (optional)

See: https://hermes-agent.nousresearch.com/docs/skills
EOF
fi

# Create memories README
if [[ "$DRY_RUN" == "true" ]]; then
    echo "[DRY RUN] Would create memories/README.md"
else
    cat > "${TARGET_DIR}/memories/README.md" <<EOF
# ${PROFILE_NAME^} Memories

This directory stores persistent memories for the ${PROFILE_NAME} profile.
Memories are managed via the \`memory\` tool and survive across sessions.

Structure:
- USER.md — User profile, preferences, boundaries (if client profile)
- memory/ — System notes, conventions, lessons learned
EOF
fi

# Create .env template
if [[ "$DRY_RUN" == "true" ]]; then
    echo "[DRY RUN] Would create .env.template"
else
    cat > "${TARGET_DIR}/.env.template" <<EOF
# Per-profile environment variables
# Copy to ~/.hermes/.env and merge with existing, or source before running hermes

# OpenRouter API Key (for fallback models)
# OPENROUTER_API_KEY=sk-or-...

# Telegram (usually set globally in ~/.hermes/.env, not per-profile)
# TELEGRAM_BOT_TOKEN=...
# TELEGRAM_ALLOWED_USERS=...  (global, includes all profile users)
EOF
fi

echo ""
echo "=== Deployment Complete ==="
echo "Profile: $PROFILE_NAME ($PROFILE_TYPE)"
echo "Location: $TARGET_DIR"
echo ""
echo "Next steps:"
echo "1. Review config: cat $TARGET_DIR/config.yaml"
echo "2. Add OpenRouter key to ~/.hermes/.env: OPENROUTER_API_KEY=sk-or-..."
echo "3. Ensure TELEGRAM_ALLOWED_USERS in ~/.hermes/.env includes: ${TELEGRAM_ID:-<client ID>}"
echo "4. Start profile: hermes --profile $PROFILE_NAME"
echo "5. Create cron jobs from: $TARGET_DIR/cron/jobs.yaml"
echo ""
echo "To create cron jobs automatically, run:"
echo "  hermes cronjob create --prompt-file $TARGET_DIR/cron/<prompt-file> --schedule <schedule> --deliver telegram:${TELEGRAM_ID:-<id>} --skills <skills>"