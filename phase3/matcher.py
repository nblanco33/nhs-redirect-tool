import re
from urllib.parse import urlparse
from .scorer import compute_confidence

from utils.file_utils import append_log_file

# ------------------------------------------------------------------
# Simple file logger (intentionally minimal, no external deps)
# ------------------------------------------------------------------
def log(message: str):
    LOG_FILE = "debug_matcher.log"
    append_log_file(LOG_FILE, message)



# ------------------------------------------------------------------
# Utility: Normalize URL by stripping scheme + domain
# ------------------------------------------------------------------
def strip_domain(url: str) -> str:
    parsed_url = urlparse(url)

    return (
        parsed_url.path
        + (f"?{parsed_url.query}" if parsed_url.query else "")
        + (f"#{parsed_url.fragment}" if parsed_url.fragment else "")
    )


# ------------------------------------------------------------------
# Utility: Extract first segment of a path
# ------------------------------------------------------------------
def extract_root(url_path: str) -> str | None:
    path_segments = url_path.strip("/").split("/")
    return path_segments[0] if path_segments else None


# ------------------------------------------------------------------
# STEP 1: Apply regex match against incoming URL
# ------------------------------------------------------------------
def apply_match(pattern: str, source_url) -> list[str] | None:
    """
    Applies the rule regex to the incoming request path.

    Note:
        IIS matching ignores leading "/"
    """
    match_result = re.match(pattern, source_url.path.lstrip("/"))

    if not match_result:
        return None

    # Normalize None groups → ""
    return [group if group is not None else "" for group in match_result.groups()]


# ------------------------------------------------------------------
# STEP 2: Evaluate rule conditions
# ------------------------------------------------------------------
def evaluate_conditions(rule: dict, source_url) -> tuple[bool, list[str]]:
    """
    Evaluates all conditions associated with a rule.

    Returns:
        (conditions_match: bool, captured_groups: list[str])
    """
    captured_condition_groups = []

    for condition in rule.get("conditions", []):
        pattern = condition["pattern"]
        negate = str(condition.get("negate")).strip().lower() == "true"
        input_type = condition["input"]

        # Resolve target value based on condition input
        if input_type == "{REQUEST_URI}":
            target_value = source_url.path
        elif input_type == "{QUERY_STRING}":
            target_value = source_url.query or ""
        elif input_type == "{HTTP_HOST}":
            target_value = source_url.netloc or ""
        else:
            target_value = ""

        condition_match = re.search(pattern, target_value)

        log(
            f"  [Condition] input={input_type} | pattern={pattern} | "
            f"negate={negate} | target='{target_value}' | match={bool(condition_match)}"
        )

        # Apply negate logic (IIS behavior)
        if negate:
            if condition_match:
                return False, []
        else:
            if not condition_match:
                return False, []

            # Capture groups if present
            if condition_match.groups():
                captured_condition_groups = [
                    group if group is not None else ""
                    for group in condition_match.groups()
                ]

    return True, captured_condition_groups


# ------------------------------------------------------------------
# STEP 3: Build expected redirect URL from rule template
# ------------------------------------------------------------------
def build_action_url(rule: dict, regex_groups: list[str], condition_groups: list[str], source_url) -> str:
    """
    Constructs the expected redirect URL based on rule template and captured groups.
    """

    url_template = rule["actionUrl"]

    # Replace {R:n} and {C:n}
    def replace_token(match):
        token_type = match.group(1)
        group_index = int(match.group(2)) - 1

        if token_type == "R":
            return regex_groups[group_index] if group_index < len(regex_groups) else ""

        if token_type == "C":
            return condition_groups[group_index] if group_index < len(condition_groups) else ""

        return ""

    url_with_groups = re.sub(r"\{([RC]):(\d+)\}", replace_token, url_template)

    # Replace {QUERY_STRING}
    if "{QUERY_STRING}" in url_with_groups:
        url_with_groups = url_with_groups.replace(
            "{QUERY_STRING}",
            source_url.query or ""
        )

    # Replace {HTTP_HOST}
    if "{HTTP_HOST}" in url_with_groups:
        url_with_groups = url_with_groups.replace(
            "{HTTP_HOST}",
            source_url.netloc or ""
        )

    # IIS behavior: appendQueryString (always append if true)
    should_append_query = rule.get("appendQueryString", False)

    if should_append_query and source_url.query:
        separator = "&" if "?" in url_with_groups else "?"
        url_with_groups = f"{url_with_groups}{separator}{source_url.query}"

    return url_with_groups


# ------------------------------------------------------------------
# MAIN: Evaluate a rule against a redirect hop
# ------------------------------------------------------------------
def match_rule(rule: dict, source_url, destination_url):
    """
    Evaluates whether a rule explains a redirect from source_url → destination_url.

    Returns:
        (
            action_match: bool,
            confidence: float,
            regex_match: bool,
            conditions_match: bool
        )
    """

    # --------------------------------------------------------------
    # STEP 1: Regex match
    # --------------------------------------------------------------
    regex_groups = apply_match(rule["match"], source_url)

    log(
        f"\n--- Rule Evaluation ----------------------------------\n"
        f"From: {source_url.geturl()}\n"
        f"To:   {destination_url.geturl()}\n"
        f"Rule: {rule['name']}\n"
        f"Regex: {rule['match']}\n"
        f"Action Template: {rule['actionUrl']}\n"
        f"------------------------------------------------------"
    )

    regex_match = regex_groups is not None
    if not regex_match:
        return False, 0.0, False, False

    # --------------------------------------------------------------
    # STEP 2: Conditions
    # --------------------------------------------------------------
    conditions_match, condition_groups = evaluate_conditions(
        rule,
        source_url
    )

    if not conditions_match:
        return False, 0.0, True, False

    # --------------------------------------------------------------
    # STEP 3: Build expected URL
    # --------------------------------------------------------------
    generated_url = build_action_url(
        rule,
        regex_groups,
        condition_groups,
        source_url
    )

    generated_clean = strip_domain(generated_url)
    actual_clean = strip_domain(destination_url.geturl())

    print(f"\n  Applying rule to -------------------------------------> {source_url.geturl()} ---> {destination_url.geturl()}")
    print(f"  Rule Name: {rule['name']} | regex: {rule['match']} | action Url: {rule['actionUrl']}")
    print(f"  Generated URL: {generated_url}")

    log(f"  [Generated URL] {generated_url}")
    log(f"  [Normalized] expected='{generated_clean}' | actual='{actual_clean}'")

    # --------------------------------------------------------------
    # STEP 4: Compare
    # --------------------------------------------------------------
    action_match = (
        actual_clean == generated_clean or
        actual_clean.rstrip("/") == generated_clean.rstrip("/")
    )

    log(f"  [Match Result] action_match={action_match}")

    # --------------------------------------------------------------
    # STEP 5: Confidence scoring
    # --------------------------------------------------------------
    confidence = compute_confidence(
        regex_match,
        action_match,
        conditions_match
    )

    log(f"  [Confidence] {confidence}")

    return action_match, confidence, regex_match, conditions_match