# URL Rewrite Analyzer Tool

## Overview

This tool analyzes real-world URL redirect behavior and correlates it with IIS rewrite rules.

It is designed to:

* Discover full redirect chains for a given set of URLs
* Measure latency impact per redirect hop
* Parse and structure rewrite rules from XML
* Match observed redirects to the rules that likely generated them
* Produce structured outputs for analysis and optimization

The tool can be executed as a standalone `.exe`, with no Python installation required.

---

## Project Structure

```
nhs-redirect-tool/
│
├── run.py                  # Entry point (CLI menu for phases)
├── utils.py                # Shared helpers (paths, IO, logging)
│
├── phase1/                 # Redirect discovery
│   ├── analyzer.py
│
├── phase2/                 # Rewrite rules processing
│   ├── xml_parser.py
│   ├── json_builder.py
│
├── phase3/                 # Matching engine
│   ├── run_phase3.py
│   ├── matcher.py
│   └── scorer.py
│
├── data/                   # Input + output files (used by exe)
│   ├── input.csv
│   ├── rewrite_rules.xml
│   ├── headers.json
│   ├── output_phase1.json
│   ├── output_phase2.json
│   ├── output_phase3.json
│   └── debug_matcher.log
│
└── dist/
    └── run.exe             # Standalone executable
```

---

## How the Executable Works

The `.exe` is built using PyInstaller and bundles the full application.

### Key behavior:

* The executable expects a `/data` folder **in the same directory**
* All inputs and outputs are read/written from that folder
* No external dependencies are required

---

## How to Run

1. Place the executable and the `data` folder together:

```
/your-folder/
│
├── run.exe
└── data/
```

2. Open a terminal in that location

3. Run:

```
run.exe
```

4. Select a phase from the menu:

```
1 → Discover redirect chains
2 → Parse rewrite rules
3 → Match redirects to rules
```

---

## Input Files

Located inside `/data`:

### `input.csv`

List of URLs to analyze

```
url
https://example.com/page1
https://example.com/page2
```

---

### `rewrite_rules.xml`

IIS rewrite rules file

---

### `headers.json`

Custom HTTP headers used for requests (optional but recommended)

Allows easy modification without changing code.

---

## Output Files

All outputs are written to `/data`:

### Phase 1 → `output_phase1.json`

* Redirect chains per URL
* Status codes
* Latency per hop

---

### Phase 2 → `output_phase2.json`

* Structured rewrite rules
* Indexed for fast lookup

---

### Phase 3 → `output_phase3.json`

* Full redirect chain traceability
* Matched rules per hop
* Confidence scoring
* Candidate rules evaluated

---

### Debug Log → `debug_matcher.log`

* Detailed rule evaluation logs
* Useful for debugging matching behavior

---

## Execution Flow

1. **Phase 1**

   * Input: `input.csv`
   * Output: redirect chains + timing

2. **Phase 2**

   * Input: `rewrite_rules.xml`
   * Output: structured rule set

3. **Phase 3**

   * Input: Phase 1 + Phase 2 outputs
   * Output: redirect-to-rule correlation

---

## Goal

Provide actionable insights to:

* Identify unnecessary redirects
* Detect performance bottlenecks
* Understand rewrite rule complexity
* Enable optimization of redirect strategies

---

## Notes

* The tool is designed for analysis, not production deployment
* Large input sets may increase execution time
* Logging can be verbose depending on rule complexity

---
