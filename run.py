# run.py

"""
URL Rewrite Analyzer Tool - Entry Point

This script orchestrates the execution of the three main phases:

Phase 1: Collect and analyze real redirect behavior
Phase 2: Parse and compile rewrite rules from XML
Phase 3: Match observed redirects to rewrite rules

Each phase can be executed independently via CLI.
"""

from utils.file_utils import (
    read_csv_rows,
    read_xml_file,
    read_json_file,
    write_json_file,
)

from phase1.analyzer import analyze_url
from phase2.xml_parser import parse_rules
from phase2.json_builder import build_json
from phase3.run_phase3 import run_phase3


# ------------------------------------------------------------------
# Phase 1: URL redirect discovery
# ------------------------------------------------------------------
def run_phase1():
    """
    Executes Phase 1:
    - Reads input URLs from CSV (via utils)
    - Transforms rows into URL list
    - Follows redirect chains
    - Stores only URLs with redirects
    """

    input_file = "input.csv"
    output_file = "output_phase1.json"
    headers_file = "headers.json"

    rows = read_csv_rows(input_file)

    if not rows:
        raise Exception("Input CSV is empty.")

    urls = [
        row[0].strip()
        for row in rows[1:]
        if row and row[0].strip()
    ]

    try:
        headers = read_json_file(headers_file)
        print(f"[Phase 1] Headers loaded from {headers_file}")
    except Exception:
        headers = {}
        print("[Phase 1] No headers file found → using default request")

    print(f"\n[Phase 1] Processing {len(urls)} URLs...\n")

    collected_results = []

    for index, url in enumerate(urls, start=1):
        analysis_result = analyze_url(url, headers)

        print(f"[{index}/{len(urls)}] {analysis_result}")

        if analysis_result.get("redirects"):
            collected_results.append(analysis_result)

    write_json_file(output_file, collected_results)

    print(f"\n[Phase 1] Completed → Results saved to data/{output_file}")


# ------------------------------------------------------------------
# Phase 2: Rewrite rules compilation
# ------------------------------------------------------------------
def run_phase2():
    """
    Executes Phase 2:
    - Loads IIS rewrite rules XML (via utils)
    - Parses rules into structured format
    - Builds optimized indexes (root-based grouping)
    - Persists compiled ruleset
    """

    input_file = "rewrite_rules.xml"
    output_file = "output_phase2.json"

    print("\n[Phase 2] Loading XML rules...")

    xml_tree = read_xml_file(input_file)
    parsed_rules = parse_rules(xml_tree)

    print(f"[Phase 2] Parsed {len(parsed_rules)} rules")

    compiled_ruleset = build_json(parsed_rules)

    write_json_file(output_file, compiled_ruleset)

    print(f"[Phase 2] Completed → Output saved to data/{output_file}")


# ------------------------------------------------------------------
# CLI Entry Point
# ------------------------------------------------------------------
def main():
    """
    Simple CLI menu to trigger each phase independently.
    """

    print(
        """
===========================
 URL Rewrite Analyzer Tool
===========================

Select an option:

1. Run Phase 1 → Discover redirects
2. Run Phase 2 → Compile rewrite rules
3. Run Phase 3 → Match redirects to rules
4. Exit
"""
    )

    user_choice = input("Your choice: ").strip()

    if user_choice == "1":
        run_phase1()

    elif user_choice == "2":
        run_phase2()

    elif user_choice == "3":
        run_phase3()

    elif user_choice == "4":
        print("\nExiting... 👋")
        return

    else:
        print("\nInvalid option. Please select a valid number.")


# ------------------------------------------------------------------
# Script execution
# ------------------------------------------------------------------
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback

        print("\n❌ An unexpected error occurred:\n")
        print(str(e))
        print("\n--- Full Traceback ---\n")
        traceback.print_exc()

    input("\nPress Enter to exit...")