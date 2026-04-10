"""
XML Rule Parser

Parses IIS rewrite rules from XML into a normalized Python structure
used by downstream phases.

Key responsibilities:
- Extract rule metadata (name, stopProcessing)
- Parse match patterns
- Parse action configuration (redirects)
- Normalize boolean attributes
- Extract and normalize conditions

Output is a list of rule dictionaries with consistent structure.
"""


def _parse_bool(value: str | None, default: bool = False) -> bool:
    """
    Safely parse a boolean-like XML attribute.

    Handles:
        "true", "True", " TRUE ", None

    Args:
        value (str | None): Raw XML attribute value
        default (bool): Default if value is None

    Returns:
        bool
    """
    if value is None:
        return default

    return str(value).strip().lower() == "true"


def parse_rules(tree) -> list[dict]:
    """
    Parses IIS rewrite rules XML into structured rule objects.

    Supports XML formats:
        - <rewrite><rules>...</rules></rewrite>
        - <rules>...</rules>

    Returns:
        list[dict]: Parsed rules with normalized structure

    Raises:
        Exception: If no <rules> section is found
    """

    xml_root = tree.getroot()

    # ------------------------------------------------------------------
    # Locate <rules> section (supports multiple XML layouts)
    # ------------------------------------------------------------------
    rules_section = xml_root.find(".//rules")

    if rules_section is None and xml_root.tag == "rules":
        rules_section = xml_root

    if rules_section is None:
        raise Exception("❌ No se encontró sección <rules> en el archivo XML.")

    parsed_rules = []

    # ------------------------------------------------------------------
    # Iterate over each <rule> node
    # ------------------------------------------------------------------
    for rule_node in rules_section.findall("rule"):

        # --------------------------------------------------------------
        # Rule metadata
        # --------------------------------------------------------------
        rule_name = rule_node.get("name")
        stop_processing = _parse_bool(rule_node.get("stopProcessing"), default=False)

        # --------------------------------------------------------------
        # MATCH: <match url="..." />
        # --------------------------------------------------------------
        match_node = rule_node.find("match")
        match_pattern = match_node.get("url") if match_node is not None else None

        # --------------------------------------------------------------
        # ACTION: <action ... />
        # --------------------------------------------------------------
        action_node = rule_node.find("action")

        action_type = action_node.get("type") if action_node is not None else None
        action_url = action_node.get("url") if action_node is not None else None

        redirect_type = (
            action_node.get("redirectType")
            if action_node is not None and action_type == "Redirect"
            else None
        )

        append_query_string = _parse_bool(
            action_node.get("appendQueryString") if action_node is not None else None,
            default=False
        )

        # --------------------------------------------------------------
        # CONDITIONS: <conditions> ... </conditions>
        # --------------------------------------------------------------
        conditions = []
        conditions_node = rule_node.find("conditions")

        track_all_captures = _parse_bool(
            conditions_node.get("trackAllCaptures") if conditions_node is not None else None,
            default=False
        )

        if conditions_node is not None:
            for condition_node in conditions_node.findall("add"):

                conditions.append({
                    "input": condition_node.get("input"),
                    "pattern": condition_node.get("pattern"),
                    "negate": _parse_bool(condition_node.get("negate"), default=False)
                })

        # --------------------------------------------------------------
        # Build normalized rule object
        # --------------------------------------------------------------
        parsed_rules.append({
            "name": rule_name,
            "stopProcessing": stop_processing,
            "match": match_pattern,
            "actionType": action_type,
            "actionUrl": action_url,
            "redirectType": redirect_type,
            "appendQueryString": append_query_string,
            "trackAllCaptures": track_all_captures,
            "conditions": conditions
        })

    return parsed_rules