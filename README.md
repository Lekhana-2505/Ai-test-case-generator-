# AI Test Case Generator

Turns a requirement, user story, API spec, or source code into a structured test suite
(ID, category, priority, preconditions, steps, test data, expected result) using Claude.
Can optionally write runnable automation code (pytest, jest, JUnit, Playwright, ...).

## Setup

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
$env:ANTHROPIC_API_KEY = "sk-ant-..."   # get a key at https://console.anthropic.com
```

## Web UI

```powershell
python app.py
```
Open http://127.0.0.1:5000, paste your input, pick categories, and click **Generate**.
Results can be downloaded as CSV (Excel / Jira / TestRail import), Markdown, or JSON.

## CLI

```powershell
python cli.py -t "Login with email + password; account locks after 5 failed attempts" -n 12
python cli.py -f path\to\cart.py --framework pytest -o cart_tests.md
python cli.py -f story.txt -c positive negative security -o cases.csv
```

## Project layout

- `testgen/models.py`: Pydantic schema for the test suite (used for structured output)
- `testgen/generator.py`: Claude API call (`claude-opus-5-5`, streaming, structured output)
- `testgen/exporters.py`: JSON / CSV / Markdown export
- `cli.py`, `app.py` + `templates/index.html`: command-line and web front ends
