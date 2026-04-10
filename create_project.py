import os

structure = {
    # Root-level files
    "run.py": "# run.py\n",

    # Phase 1
    "phase1/reader.py": "# reader.py\n",
    "phase1/analyzer.py": "# analyzer.py\n",
    "phase1/writer.py": "# writer.py\n",
    "phase1/__init__.py": "",
    "phase1/headers.py": "# headers.py\n",

    # Phase 2
    "phase2/xml_loader.py": "# xml_loader.py\n",
    "phase2/xml_parser.py": "# xml_parser.py\n",
    "phase2/json_builder.py": "# json_builder.py\n",
    "phase2/writer.py": "# writer.py\n",
    "phase2/__init__.py": "",

    # Phase 3
    "phase3/matcher.py": "# matcher.py\n",
    "phase3/scorer.py": "# scorer.py\n",
    "phase3/run_phase3.py": "# run_phase3.py\n",
    "phase3/__init__.py": "",

    # Data folder
    "data/input.csv": "",
    "data/rewrite_rules.xml": "",
    "data/output_phase1.json": "",
    "data/output_phase2.json": "",
    "data/summary_phase2.json": "",
    "data/output_phase3.json": "",
}

def ensure_dirs():
    for path in structure.keys():
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def create_files():
    for path, content in structure.items():
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Created file: {path}")
        else:
            print(f"Skipping existing file: {path}")

def main():
    ensure_dirs()
    create_files()
    print("\nSAFE PROJECT STRUCTURE CREATED SUCCESSFULLY!")

if __name__ == "__main__":
    main()