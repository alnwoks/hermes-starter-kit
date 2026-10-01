#!/usr/bin/env python3
"""
generate.py — Client questionnaire → starter-kit-based deployment
Usage:
  python3 generate.py --client clients/blessing.yaml --env production
Output: ~/.hermes/profiles/<name>/config.yaml + memories/USER.md + deployed profile
"""
import argparse
import yaml
import subprocess
from pathlib import Path

KIT_DIR = Path("hermes-starter-kit")


def deploy_client(config_path: Path, env: str):
    data = yaml.safe_load(config_path.read_text())

    print(f"=== Deploying Client Profile: {data['profile_name']} ===")
    print(f"Client: {data['client_name']}")
    print(f"Role: {data['client_role']}")
    print(f"Transition: {data['client_transition']}")

    # Step 1: Deploy profile from starter kit
    deploy_cmd = [
        "python3", str(KIT_DIR / "scripts" / "deploy_profile.py"),
        data["profile_name"], "client",
        "--telegram-id", str(data.get("telegram_id", "")),
        "--telegram-chats", str(data.get("telegram_chats", "")),
        "--home-channel", str(data.get("home_channel", "")),
        "--client-name", str(data["client_name"]),
        "--client-role", str(data.get("client_role", "Client")),
        "--client-transition", str(data.get("client_transition", "")),
        "--client-priorities", str(data.get("client_priorities", "")),
    ]
    # Filter empty args
    deploy_cmd = [str(x) for x in deploy_cmd if x != ""]
    subprocess.run(deploy_cmd, check=True)

    # Step 2: Write USER.md from questionnaire responses
    memories_dir = Path.home() / ".hermes" / "profiles" / data["profile_name"] / "memories"
    memories_dir.mkdir(parents=True, exist_ok=True)

    user_md = f"""## User Profile — {data['client_name']}
- Role: {data.get('client_role', 'Not specified')} → {data.get('client_transition', 'Not specified')}
- Typical work: {data.get('typical_work', 'Not specified')}
- Biggest time sinks: {data.get('time_sinks', 'Not specified')}
- Core needs: {data.get('core_needs', 'Not specified')}
- Pain points: {data.get('pain_points', 'Not specified')}

## Communication Preferences
- Format: {data.get('format_pref', 'Concise structured bullets')}
- Tone: {data.get('tone_pref', 'Friendly, direct, practical')}
- Proactivity level: {data.get('proactivity', 'Very proactive')}
- Uncertainty handling: {data.get('uncertainty_pref', 'Ask when important; assume when low-risk')}

## Boundaries (never without approval)
{chr(10).join(data.get('boundaries', ['Not specified']))}

## Current Priorities
{chr(10).join(data.get('priorities_list', ['Not specified']))}

## Working Style
{data.get('working_style', 'Not specified')}

## Client Context (Initial Questionnaire)
### What do you do daily?
{data.get('daily_work', 'Not specified')}

### What's taking too much time?
{data.get('time_sinks', 'Not specified')}

### What are you trying to become/achieve?
{data.get('transition_goal', 'Not specified')}

### What's blocking you?
{data.get('blockers', 'Not specified')}
"""
    (memories_dir / "USER.md").write_text(user_md)
    print(f"Memory profile written: {memories_dir / 'USER.md'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--client", required=True, help="Path to client YAML config")
    parser.add_argument("--env", default="production", help="Environment (production/staging)")
    args = parser.parse_args()
    deploy_client(Path(args.client), args.env)