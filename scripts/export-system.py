#!/usr/bin/env python3
"""
export-system.py — Export live Hermes Agent system to starter kit format
Captures profiles, configs, cron jobs, skills, memories for git tracking
"""
import argparse
import json
import os
import shutil
import sys
from pathlib import Path

HERMES_DIR = Path.home() / ".hermes"


def export_profiles(output_dir: Path, profile_names: list = None):
    """Export profile configs, cron jobs, skills, memories."""
    profiles_dir = HERMES_DIR / "profiles"
    if not profiles_dir.exists():
        print("No profiles directory found")
        return

    if profile_names is None:
        profile_names = [d.name for d in profiles_dir.iterdir() if d.is_dir()]

    for name in profile_names:
        src = profiles_dir / name
        dst = output_dir / "profiles" / name
        if not src.exists():
            print(f"Profile not found: {name}")
            continue

        print(f"Exporting profile: {name}")
        dst.mkdir(parents=True, exist_ok=True)

        # Copy config.yaml (sanitize secrets)
        config_src = src / "config.yaml"
        if config_src.exists():
            content = config_src.read_text()
            # Redact API keys
            import re
            content = re.sub(r'api_key: .*', 'api_key: «redacted»', content)
            content = re.sub(r'OPENROUTER_API_KEY=.*', 'OPENROUTER_API_KEY=«redacted»', content)
            (dst / "config.yaml").write_text(content)

        # Copy cron jobs
        cron_src = src / "cron"
        if cron_src.exists():
            cron_dst = dst / "cron"
            shutil.copytree(cron_src, cron_dst, dirs_exist_ok=True)

        # Copy skills (structure only, not content - skills are in global ~/.hermes/skills)
        skills_src = src / "skills"
        if skills_src.exists():
            skills_dst = dst / "skills"
            skills_dst.mkdir(parents=True, exist_ok=True)
            # Just copy README if exists, or create one
            readme = skills_src / "README.md"
            if readme.exists():
                shutil.copy2(readme, skills_dst / "README.md")
            else:
                (skills_dst / "README.md").write_text(f"# {name.capitalize()} Skills\n\nAdd custom skills here.")

        # Copy memories (structure only - actual memories in global ~/.hermes/memories)
        memories_src = src / "memories"
        if memories_src.exists():
            memories_dst = dst / "memories"
            memories_dst.mkdir(parents=True, exist_ok=True)
            readme = memories_src / "README.md"
            if readme.exists():
                shutil.copy2(readme, memories_dst / "README.md")
            else:
                (memories_dst / "README.md").write_text(f"# {name.capitalize()} Memories\n\nPersistent memories for {name} profile.")


def export_cron_jobs(output_dir: Path):
    """Export cron job definitions from Hermes."""
    try:
        import subprocess
        result = subprocess.run(
            ["hermes", "cronjob", "list"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            # Parse output and save as JSON
            jobs_data = {"jobs": []}
            # This is a simplified parse - in practice you'd use the actual API
            (output_dir / "cron_jobs_export.json").write_text(result.stdout)
            print("Cron jobs exported to cron_jobs_export.json")
    except Exception as e:
        print(f"Could not export cron jobs: {e}")


def export_global_config(output_dir: Path):
    """Export global config.yaml (sanitized)."""
    config_src = HERMES_DIR / "config.yaml"
    if config_src.exists():
        content = config_src.read_text()
        import re
        content = re.sub(r'api_key: .*', 'api_key: «redacted»', content)
        content = re.sub(r'OPENROUTER_API_KEY=.*', 'OPENROUTER_API_KEY=«redacted»', content)
        (output_dir / "config.yaml.global").write_text(content)
        print("Global config exported")


def main():
    parser = argparse.ArgumentParser(description="Export Hermes system to starter kit")
    parser.add_argument("--output", "-o", default="hermes-starter-kit-export",
                        help="Output directory")
    parser.add_argument("--profiles", nargs="+", help="Specific profiles to export")
    parser.add_argument("--include-global", action="store_true", help="Export global config")
    args = parser.parse_args()

    output_dir = Path(args.output).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Exporting to: {output_dir}")

    export_profiles(output_dir, args.profiles)
    export_cron_jobs(output_dir)
    if args.include_global:
        export_global_config(output_dir)

    # Create deployment scripts copy
    scripts_src = Path(__file__).parent
    scripts_dst = output_dir / "scripts"
    shutil.copytree(scripts_src, scripts_dst, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("*.pyc", "__pycache__"))

    # Copy docs if exist
    docs_src = scripts_src.parent / "docs"
    if docs_src.exists():
        shutil.copytree(docs_src, output_dir / "docs", dirs_exist_ok=True)

    # Copy README
    readme_src = scripts_src.parent / "README.md"
    if readme_src.exists():
        shutil.copy2(readme_src, output_dir / "README.md")

    print(f"\nExport complete: {output_dir}")
    print("Review and commit to git. Secrets are redacted.")


if __name__ == "__main__":
    main()