from urllib.parse import urlparse, urlunparse
from .matcher import match_rule

from utils.file_utils import read_json_file, write_json_file

BASE_SCHEME = "https"
BASE_NETLOC = "www.newhomesource.com"


def extract_root(path: str) -> str | None:
    """
    Extract the first path segment (root) from a URL path.

    Example:
        "/learn/news/article" -> "learn"

    Returns:
        str | None: Root segment or None if path is empty.
    """
    if not path:
        return None

    normalized_path = path.lstrip("/")

    if not normalized_path:
        return None

    return normalized_path.split("/")[0]


def run_phase3():
    """
    Phase 3: Redirect Chain → Rule Matching Engine

    This phase analyzes redirect chains step-by-step and attempts to match
    each hop against known rewrite rules.

    Key behavior:
    - Each hop is evaluated independently (no early termination of chain)
    - Best matching rule is selected per hop
    - If no rule matches → matched_rule = None
    - Confidence score reflects match quality

    Output:
        data/output_phase3.json
    """

    print("Running Phase 3...")

    # ------------------------------------------------------------------
    # Load input data (via utils)
    # ------------------------------------------------------------------
    phase1_data = read_json_file("output_phase1.json")
    phase2_data = read_json_file("output_phase2.json")

    rules = phase2_data["rules"]

    # Optional optimization structures (if present)
    root_index = phase2_data.get("rootIndex", {})
    rules_without_root = phase2_data.get("noRootRules", [])

    # ------------------------------------------------------------------
    # Debug visibility
    # ------------------------------------------------------------------
    print("\nRoot index loaded:")
    for root_key, rule_ids in root_index.items():
        print(f"  {root_key}: {len(rule_ids)} rules")

    print(f"Rules without root: {len(rules_without_root)}")

    results = []

    # ------------------------------------------------------------------
    # Process each URL entry
    # ------------------------------------------------------------------
    for entry in phase1_data:

        original_url = entry["url"]
        final_url = entry["final_url"]

        parsed_original_url = urlparse(original_url)

        redirect_chain_output = []
        previous_hop_url = parsed_original_url

        print(
            f"\n--- Processing URL -------------------------------------------------------------------------------------------\n"
            f"Original: {original_url}\n"
            f"Final: {final_url}\n"
            f"----------------------------------------------------------------------------------------------------------------"
        )

        # ------------------------------------------------------------------
        # Evaluate each hop independently
        # ------------------------------------------------------------------
        for step_number, hop in enumerate(entry["redirects"], start=1):

            hop_status = hop["status"]
            destination_url = hop["location"]

            parsed = urlparse(destination_url)
            normalized_url = urlunparse((
                BASE_SCHEME,
                BASE_NETLOC,
                parsed.path or "",
                parsed.params or "",
                parsed.query or "",
                parsed.fragment or ""
            ))

            parsed_destination_url = urlparse(normalized_url)

            # Extract root from destination (more accurate per hop)
            root = extract_root(previous_hop_url.path)

            # 1. Try root-based rules first (high precision)
            candidate_rule_ids = root_index.get(root, [])

            # 2. If no root match → fallback to rules without root
            if not candidate_rule_ids:
                candidate_rule_ids = rules_without_root

            # 3. If still empty → fallback to all redirect rules
            if not candidate_rule_ids:
                candidate_rule_ids = [
                    idx for idx, rule in enumerate(rules)
                    if rule["actionType"] == "Redirect"
                ]

            print("\n root {} → {} candidate rules".format(
                f'"{root}"' if root else "None", len(candidate_rule_ids))
            )

            candidates = []
            best_confidence = 0.0

            # --------------------------------------------------------------
            # Evaluate candidate rules for THIS hop only
            # --------------------------------------------------------------
            for rule_id in candidate_rule_ids:
                rule = rules[rule_id]

                action_match, confidence, regex_match, conditions_match = match_rule(
                    rule,
                    previous_hop_url,
                    parsed_destination_url
                )

                # Keep only meaningful candidates
                if confidence > 0:
                    candidates.append({
                        "rule_name": rule["name"],
                        "regex_match": regex_match,
                        "action_match": action_match,
                        "conditions_match": conditions_match,
                        "confidence": confidence
                    })

                # Early exit ONLY for rule evaluation (not chain)
                if confidence == 1.0:
                    best_confidence = confidence
                    break

                if confidence > best_confidence:
                    best_confidence = confidence

            # --------------------------------------------------------------
            # Select best candidates
            # --------------------------------------------------------------
            best_candidates = [
                candidate for candidate in candidates
                if candidate["confidence"] == best_confidence
            ]

            matched_rule = None

            # Assign rule ONLY if perfect match
            if best_confidence >= 1.0 and best_candidates:
                best_rule_name = best_candidates[0]["rule_name"]

                matched_rule = next(
                    (rule for rule in rules if rule["name"] == best_rule_name),
                    None
                )

            # --------------------------------------------------------------
            # Append hop result (even if no match)
            # --------------------------------------------------------------
            redirect_chain_output.append({
                "step": step_number,
                "status": hop_status,
                "from": previous_hop_url.geturl(),
                "to": parsed_destination_url.geturl(),
                "matched_rule": matched_rule,
                "confidence": best_confidence,
                "candidates": best_candidates
            })

            # Move forward in the chain
            previous_hop_url = parsed_destination_url

        # ------------------------------------------------------------------
        # Aggregate result per URL
        # ------------------------------------------------------------------
        results.append({
            "original_url": original_url,
            "final_url": final_url,
            "total_redirects": len(entry["redirects"]),
            "redirect_chain": redirect_chain_output
        })

    # ------------------------------------------------------------------
    # Persist results (via utils)
    # ------------------------------------------------------------------
    write_json_file("output_phase3.json", results)

    print("\nPhase 3 completed → data/output_phase3.json created.")