from typing import List, Optional

from .policy_models import TerminalPolicy, CommandPolicy, MatchResult


def match_command(
    policy: TerminalPolicy,
    tokens: List[str],
) -> MatchResult:
    """
    Match a tokenized command against the terminal allow-list policy.

    Args:
        policy: Loaded TerminalPolicy
        tokens: Tokenized command (e.g. ["aws","sts","get-caller-identity"])

    Returns:
        MatchResult
    """
    if not tokens:
        return MatchResult(
            allowed=False,
            policy_id=None,
            reason="empty_command",
        )

    executable = tokens[0]
    args = tokens[1:]

    for category in policy.categories.values():
        for cmd in category.commands:

            # Executable must match exactly
            if executable != cmd.executable:
                continue

            # argv prefix must match exactly
            if args[: len(cmd.argv)] != cmd.argv:
                continue

            remaining_args = args[len(cmd.argv):]

            # Enforce deny flags
            for flag in cmd.deny_flags:
                if flag in remaining_args:
                    return MatchResult(
                        allowed=False,
                        policy_id=cmd.id,
                        reason=f"flag_not_allowed:{flag}",
                    )

            # Enforce required flags
            for flag in cmd.require_flags:
                if flag not in remaining_args:
                    return MatchResult(
                        allowed=False,
                        policy_id=cmd.id,
                        reason=f"missing_required_flag:{flag}",
                    )

            # Enforce output formats (if defined)
            if cmd.output_formats:
                if "--output" in remaining_args:
                    idx = remaining_args.index("--output")
                    try:
                        value = remaining_args[idx + 1]
                    except IndexError:
                        return MatchResult(
                            allowed=False,
                            policy_id=cmd.id,
                            reason="output_flag_missing_value",
                        )

                    if value not in cmd.output_formats:
                        return MatchResult(
                            allowed=False,
                            policy_id=cmd.id,
                            reason=f"output_format_not_allowed:{value}",
                        )

            return MatchResult(
                allowed=True,
                policy_id=cmd.id,
                reason=None,
            )

    return MatchResult(
        allowed=False,
        policy_id=None,
        reason="command_not_allowed",
    )
