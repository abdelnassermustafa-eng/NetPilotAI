from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class CommandPolicy:
    id: str
    executable: str
    argv: List[str]
    allow_flags: List[str] = field(default_factory=list)
    require_flags: List[str] = field(default_factory=list)
    deny_flags: List[str] = field(default_factory=list)
    output_formats: List[str] = field(default_factory=list)
    allow_wildcards: bool = False
    audit: Dict[str, str] = field(default_factory=dict)


@dataclass
class CategoryPolicy:
    name: str
    title: str
    provider: str
    commands: List[CommandPolicy]


@dataclass
class TerminalPolicy:
    version: str
    policy_name: str
    description: str
    defaults: Dict[str, object]
    categories: Dict[str, CategoryPolicy]

@dataclass
class MatchResult:
    allowed: bool
    policy_id: Optional[str]
    reason: Optional[str]


