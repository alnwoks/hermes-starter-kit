#!/usr/bin/env python3
"""
deploy_profile.py — Deploy Hermes Agent profiles from starter kit
Cross-platform Python version of deploy-profile.sh
"""
import argparse
import os
import shutil
import sys
from pathlib import Path
from string import Template

KIT_DIR = Path(__file__).parent.parent
HERMES_DIR = Path.home() / ".hermes"


def parse_args():
    parser = argparse.ArgumentParser(description="Deploy Hermes Agent profile from starter kit")
    parser.add_argument("profile_name", help="Profile name (e.g., blessing, john, sarah)")
    parser.add_argument("profile_type", choices=["admin", "client"], help="Profile type")
    parser.add_argument("--telegram-id", help="User Telegram ID")
    parser.add_argument("--telegram-chats", help="Comma-separated allowed chat IDs")
    parser.add_argument("--home-channel", help="TELEGRAM_HOME_CHANNEL (admin user ID)")
    parser.add_argument("--openrouter-key", help="OpenRouter API key")
    parser.add_argument("--client-name", help="Client display name (client profiles)")
    parser.add_argument("--client-role", help="Client current role (client profiles)")
    parser.add_argument("--client-transition", help="Client transition goal (client profiles)")
    parser.add_argument("--client-priorities", help="Client priorities comma-separated (client profiles)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    return parser.parse_args()


def substitute_template(content: str, substitutions: dict) -> str:
    """Simple template substitution for {{VAR}} patterns."""
    for key, value in substitutions.items():
        content = content.replace(f"{{{{{key}}}}}", str(value))
    return content


def deploy_profile(args):
    template_dir = KIT_DIR / "profiles" / f"{args.profile_type}-template"
    target_dir = HERMES_DIR / "profiles" / args.profile_name

    if not template_dir.exists():
        print(f"Error: Template not found: {template_dir}", file=sys.stderr)
        return 1

    print(f"=== Deploying {args.profile_type} profile: {args.profile_name} ===")
    print(f"Source: {template_dir}")
    print(f"Target: {target_dir}")

    if args.dry_run:
        print("[DRY RUN] Would create directories and process files")
        return 0

    # Create target directories
    for subdir in ["skills", "cron", "memories"]:
        (target_dir / subdir).mkdir(parents=True, exist_ok=True)

    # Prepare substitutions
    subs = {}
    if args.profile_type == "admin":
        admin_id = args.telegram_id or args.home_channel or ""
        subs["ADMIN_TELEGRAM_ID"] = admin_id
    else:
        subs["CLIENT_TELEGRAM_ID"] = args.telegram_id or ""
        subs["CLIENT_NAME"] = args.client_name or args.profile_name
        subs["CLIENT_ROLE"] = args.client_role or "Client"
        subs["CLIENT_TRANSITION"] = args.client_transition or "Automation/AI transition"
        subs["CLIENT_PRIORITIES"] = args.client_priorities or "Automation skills, professional growth, productivity systems"

    # Process config.yaml
    config_src = template_dir / "config.yaml"
    config_dst = target_dir / "config.yaml"
    config_content = config_src.read_text()

    # Handle telegram.allowed_chats and TELEGRAM_HOME_CHANNEL
    if args.telegram_chats:
        config_content = config_content.replace(
            'telegram:\n  allowed_chats: ""',
            f'telegram:\n  allowed_chats: "{args.telegram_chats}"'
        )
    home_channel = args.home_channel or (args.telegram_id if args.profile_type == "admin" else "")
    if home_channel:
        config_content = config_content.replace(
            'TELEGRAM_HOME_CHANNEL: ""',
            f'TELEGRAM_HOME_CHANNEL: {home_channel}'
        )

    config_content = substitute_template(config_content, subs)
    config_dst.write_text(config_content)
    print(f"Config written: {config_dst}")

    # Copy and process cron jobs
    cron_src = template_dir / "cron"
    cron_dst = target_dir / "cron"
    shutil.copytree(cron_src, cron_dst, dirs_exist_ok=True)

    if args.profile_type == "client":
        for prompt_file in cron_dst.glob("*.prompt"):
            content = prompt_file.read_text()
            content = substitute_template(content, subs)
            prompt_file.write_text(content)
    print(f"Cron jobs copied to: {cron_dst}")

    # Create skills README
    (target_dir / "skills" / "README.md").write_text(f"""# {args.profile_name.capitalize()} Skills

Add custom skills here. Each skill should have:
- SKILL.md (definition)
- references/ (optional)
- templates/ (optional)
- scripts/ (optional)

See: https://hermes-agent.nousresearch.com/docs/skills
""")

    # Create memories README
    (target_dir / "memories" / "README.md").write_text(f"""# {args.profile_name.capitalize()} Memories

This directory stores persistent memories for the {args.profile_name} profile.
Memories are managed via the `memory` tool and survive across sessions.

Structure:
- USER.md — User profile, preferences, boundaries (if client profile)
- memory/ — System notes, conventions, lessons learned
""")

    # Create .env template
    (target_dir / ".env.template").write_text("""# Per-profile environment variables
# Copy to ~/.hermes/.env and merge with existing, or source before running hermes

# OpenRouter API Key (for fallback models)
# OPENROUTER_API_KEY=sk-or-...

# Telegram (usually set globally in ~/.hermes/.env, not per-profile)
# TELEGRAM_BOT_TOKEN=...
# TELEGRAM_ALLOWED_USERS=...  (global, includes all profile users)
""")

    print(f"\n=== Deployment Complete ===")
    print(f"Profile: {args.profile_name} ({args.profile_type})")
    print(f"Location: {target_dir}")
    print(f"\nNext steps:")
    print(f"1. Review config: cat {target_dir}/config.yaml")
    print(f"2. Add OpenRouter key to ~/.hermes/.env: OPENROUTER_API_KEY=sk-or-...")
    print(f"3. Ensure TELEGRAM_ALLOWED_USERS in ~/.hermes/.env includes: {args.telegram_id or '<client ID>'}")
    print(f"4. Start profile: hermes --profile {args.profile_name}")
    print(f"5. Create cron jobs from: {target_dir}/cron/jobs.yaml")

    return 0


if __name__ == "__main__":
    sys.exit(deploy_profile(parse_args()))