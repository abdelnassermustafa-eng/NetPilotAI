import yaml
from pathlib import Path
from typing import Dict

from .policy_models import (
    TerminalPolicy,
    CategoryPolicy,
    CommandPolicy,
)


class PolicyLoadError(Exception):
    pass


def load_terminal_policy(path: Path) -> TerminalPolicy:
    if not path.exists():
        raise PolicyLoadError(f"Policy file not found: {path}")

    with path.open() as f:
        raw = yaml.safe_load(f)

    try:
        categories: Dict[str, CategoryPolicy] = {}

        for cmd in raw.get("commands", []):
            category_name = cmd.get("category", "uncategorized")

            if category_name not in categories:
                categories[category_name] = CategoryPolicy(
                    name=category_name,
                    title=category_name.replace("_", " ").title(),
                    provider=cmd.get("provider", "unknown"),
                    commands=[],
                )

            categories[category_name].commands.append(
                CommandPolicy(
                    id=cmd["id"],
                    executable=cmd["executable"],
                    argv=cmd.get("args", []),
                    allow_flags=cmd.get("allow_flags", []),
                    require_flags=cmd.get("require_flags", []),
                    deny_flags=cmd.get("deny_flags", []),
                    output_formats=cmd.get("output_formats", []),
                    allow_wildcards=cmd.get("allow_wildcards", False),
                    audit={
                        "risk": cmd.get("risk", "unknown"),
                        "read_only": str(cmd.get("read_only", True)),
                    },
                )
            )

        return TerminalPolicy(
            version=str(raw.get("version")),
            policy_name=raw.get("policy_name", "terminal-allowlist-v2"),
            description=raw.get("description", ""),
            defaults=raw.get("defaults", {}),
            categories=categories,
        )

    except KeyError as e:
        raise PolicyLoadError(f"Invalid policy format, missing key: {e}")


def load_policy(path: str) -> TerminalPolicy:
    """
    Public loader entry point for terminal allow-list policy.
    Accepts string paths for convenience.
    """
    return load_terminal_policy(Path(path))


