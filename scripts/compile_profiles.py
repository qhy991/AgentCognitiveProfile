#!/usr/bin/env python3
"""Compile cognitive profile YAML definitions into CLAUDE.md variant files.

Usage:
    python scripts/compile_profiles.py              # generate all
    python scripts/compile_profiles.py --profile p011  # single profile

Each profile YAML in profiles/ describes a cognitive vector (0/1 on 3 axes)
and a set of detailed behavioral rules. The compiler reads these rules and
generates a complete CLAUDE.md file that will be injected into the agent's
workspace as its memory/personality file.

The generated files are written to variants/ and are directly usable by
run_experiment.py.
"""

import argparse
import sys
from pathlib import Path

import yaml  # pip install pyyaml

ROOT = Path(__file__).resolve().parent.parent
PROFILES_DIR = ROOT / "profiles"
VARIANTS_DIR = ROOT / "variants"

HEADER = """# CLAUDE.md

## Project notes

This workspace contains a small, self-contained Python project. The task
prompt describes what needs to be done. Use the standard library only, and
run tests with `pytest` if test files are present. Keep the existing file
layout unless the task requires otherwise.

## How you work

Follow this working style at all times:

"""


def compile_profile(profile: dict) -> str:
    """Compile a single profile dict into a complete CLAUDE.md string."""
    rules = profile.get("rules", [])
    rules_text = "\n".join(f"- {rule}" for rule in rules)
    return HEADER + rules_text + "\n"


def compile_all():
    """Compile all profiles in profiles/ and write to variants/."""
    VARIANT_DIR = ROOT / "variants"
    VARIANT_DIR.mkdir(parents=True, exist_ok=True)

    compiled = []
    for yaml_path in sorted(PROFILES_DIR.glob("p*.yaml")):
        profile = yaml.safe_load(yaml_path.read_text())
        output = compile_profile(profile)
        out_path = VARIANT_DIR / f"{profile['id']}_{profile['name'].lower().replace(' ', '_')}.md"
        out_path.write_text(output)
        vec = profile["vector"]
        print(f"  {profile['id']} {profile['name']:<28} "
              f"E={vec['exploration']} T={vec['thinking']} A={vec['adaptation']} "
              f"→ {out_path.name}")
        compiled.append(profile)

    print(f"\n{len(compiled)} profiles compiled to {VARIANT_DIR}/")
    return compiled


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--profile", help="compile a single profile by id (e.g. p011)")
    args = ap.parse_args()

    if args.profile:
        yaml_path = PROFILES_DIR / f"{args.profile}_*.yaml"
        matches = list(PROFILES_DIR.glob(f"{args.profile}_*.yaml"))
        if not matches:
            raise SystemExit(f"profile {args.profile} not found in {PROFILES_DIR}")
        profile = yaml.safe_load(matches[0].read_text())
        print(compile_profile(profile))
    else:
        compile_all()


if __name__ == "__main__":
    main()