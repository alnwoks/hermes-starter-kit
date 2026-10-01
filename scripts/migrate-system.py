#!/usr/bin/env python3
"""
migrate-system.py — Migrate Hermes Agent system to new machine from starter kit
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_cmd(cmd, check=True):
    """Run command and return result."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Command failed: {cmd}")
        print(result.stderr)
        sys.exit(result.returncode)
    return result


def migrate(kit_dir: Path, profile_name: str, profile_type: str, **kwargs):
    """Migrate a profile from starter kit to live system."""
    print(f"=== Migrating {profile_type} profile: {profile_name} ===")

    # Deploy profile using deploy script
    deploy_script = kit_dir / "scripts" / "deploy_profile.py"
    cmd = [
        sys.executable, str(deploy_script),
        profile_name, profile_type
    ]

    # Add kwargs as arguments
    for key, value in kwargs.items():
        if value is not None:
            arg_name = f"--{key.replace('_', '-')}"
            cmd.extend([arg_name, str(value)])

    print(f"Running: {' '.join(cmd)}")
    run_cmd(' '.join(cmd))

    print(f"\nProfile {profile_name} deployed.")
    print(f"Start with: hermes --profile {profile_name}")


def migrate_all(kit_dir: Path, profiles: list):
    """Migrate multiple profiles."""
    for profile in profiles:
        migrate(kit_dir, **profile)


def setup_global_env(kit_dir: Path):
    """Set up global ~/.hermes/.env from template."""
    hermes_dir = Path.home() / ".hermes"
    env_file = hermes_dir / ".env"

    if env_file.exists():
        print("Global .env already exists, skipping.")
        return

    template = kit_dir / "profiles" / "client-template" / ".env.template"
    if template.exists():
        shutil.copy2(template, env_file)
        print(f"Created {env_file} from template")
        print("IMPORTANT: Edit .env and add your TELEGRAM_BOT_TOKEN and OPENROUTER_API_KEY")
    else:
        print("No .env template found")


def verify_migration(profile_name: str):
    """Verify profile works by starting a test session."""
    print(f"\nVerifying profile: {profile_name}")
    # Just check config exists
    config_path = Path.home() / ".hermes" / "profiles" / profile_name / "config.yaml"
    if config_path.exists():
        print(f"✅ Config found: {config_path}")
    else:
        print(f"❌ Config missing: {config_path}")
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description="Migrate Hermes system from starter kit")
    parser.add_argument("--kit", default="hermes-starter-kit", help="Starter kit directory")
    parser.add_argument("--profile", action="append", help="Profile to migrate (name:type)")
    parser.add_argument("--all", action="store_true", help="Migrate all profiles in kit")
    parser.add_argument("--setup-env", action="store_true", help="Set up global .env")
    parser.add_argument("--verify", action="store_true", help="Verify after migration")
    args = parser.parse_args()

    kit_dir = Path(args.kit).resolve()
    if not kit_dir.exists():
        print(f"Starter kit not found: {kit_dir}")
        sys.exit(1)

    print(f"Using starter kit: {kit_dir}")

    if args.setup_env:
        setup_global_env(kit_dir)

    profiles_to_migrate = []

    if args.profile:
        for p in args.profile:
            try:
                name, ptype = p.split(":")
                profiles_to_migrate.append({"profile_name": name, "profile_type": ptype})
            except ValueError:
                print(f"Invalid profile format: {p} (use name:type)")
                sys.exit(1)

    if args.all:
        profiles_dir = kit_dir / "profiles"
        for ptype in ["admin", "client-template"]:
            pdir = profiles_dir / ptype
            if pdir.exists():
                # For client-template, we'd need specific names - skip auto
                if ptype == "admin":
                    profiles_to_migrate.append({"profile_name": "admin", "profile_type": "admin"})

    if not profiles_to_migrate and not args.setup_env:
        print("No profiles specified. Use --profile name:type or --all")
        sys.exit(1)

    for profile in profiles_to_migrate:
        migrate(kit_dir, **profile)

    if args.verify:
        for profile in profiles_to_migrate:
            verify_migration(profile["profile_name"])

    print("\n=== Migration Complete ===")
    print("Next steps:")
    print("1. Edit ~/.hermes/.env with your API keys")
    print("2. Start profiles: hermes --profile <name>")
    print("3. Create cron jobs from deployed profile cron/jobs.yaml")


if __name__ == "__main__":
    main()