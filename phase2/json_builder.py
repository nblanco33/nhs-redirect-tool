from collections import defaultdict


def extract_root_from_pattern(pattern: str) -> str | None:
    """
    Extracts the first path segment ("root") from a rule match pattern.

    This is used to group rules for faster lookup during Phase 3.

    Limitations:
    - Only supports simple patterns (e.g., "^learn/news/...")
    - Ignores patterns with regex complexity in the first segment

    Examples:
        "^learn/news/.*"      -> "learn"
        "^(learn|news)/.*"    -> None  (complex regex)
        None                  -> None

    Returns:
        str | None: Extracted root or None if not applicable
    """
    if not pattern:
        return None

    # Remove leading anchor if present
    normalized_pattern = pattern[1:] if pattern.startswith("^") else pattern

    first_segment = normalized_pattern.split("/")[0]

    # Skip complex regex patterns in root segment
    if any(char in first_segment for char in ["(", "[", ".", "+", "*", "?"]):
        return None

    return first_segment


def build_json(rules: list[dict]) -> dict:
    """
    Compiles parsed rewrite rules into an optimized JSON structure.

    Responsibilities:
    - Generate summary metrics (rule counts by action type)
    - Build root-based index for fast rule lookup (Phase 3 optimization)
    - Separate rules that cannot be indexed by root

    Output structure:
        {
            "summary": { "Redirect": 123, ... },
            "rules": [...],
            "rootIndex": {
                "learn": [0, 4, 10],
                "news": [1, 3]
            },
            "noRootRules": [2, 5, 8]
        }

    Design decisions:
    - Only "Redirect" rules are indexed (others are ignored in Phase 3)
    - Root indexing improves performance by reducing candidate rule space
    - Complex regex patterns fall back to "noRootRules"

    Args:
        rules (list[dict]): Parsed rules from XML

    Returns:
        dict: Compiled ruleset with indexes and metadata
    """

    rule_summary = defaultdict(int)

    # Root-based index: { root -> [rule_ids] }
    root_index = defaultdict(list)

    # Rules that cannot be indexed (fallback bucket)
    rules_without_root = []

    for rule_index, rule in enumerate(rules):
        action_type = rule["actionType"]

        # Track summary metrics
        rule_summary[action_type] += 1

        # Only index redirect rules (Phase 3 only evaluates redirects)
        if action_type != "Redirect":
            continue

        root = extract_root_from_pattern(rule.get("match"))

        if root:
            root_index[root].append(rule_index)
        else:
            rules_without_root.append(rule_index)

    return {
        "summary": dict(rule_summary),
        "rules": rules,
        "rootIndex": dict(root_index),
        "noRootRules": rules_without_root
    }