import csv
import io

from .models import TestSuite


def to_json(suite: TestSuite) -> str:
    return suite.model_dump_json(indent=2)


def to_csv(suite: TestSuite) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["ID", "Title", "Category", "Priority", "Preconditions", "Steps", "Test Data", "Expected Result"])
    for tc in suite.test_cases:
        writer.writerow([
            tc.id,
            tc.title,
            tc.category,
            tc.priority,
            "\n".join(tc.preconditions),
            "\n".join(f"{i}. {s}" for i, s in enumerate(tc.steps, 1)),
            tc.test_data,
            tc.expected_result,
        ])
    return buf.getvalue()


def to_markdown(suite: TestSuite) -> str:
    lines = ["# Test Suite", "", suite.summary, ""]
    if suite.assumptions:
        lines += ["## Assumptions", ""] + [f"- {a}" for a in suite.assumptions] + [""]
    lines += ["## Test Cases", ""]
    for tc in suite.test_cases:
        lines += [f"### {tc.id}: {tc.title}", "", f"**Category:** {tc.category} | **Priority:** {tc.priority}", ""]
        if tc.preconditions:
            lines += ["**Preconditions:**"] + [f"- {p}" for p in tc.preconditions] + [""]
        lines += ["**Steps:**"] + [f"{i}. {s}" for i, s in enumerate(tc.steps, 1)] + [""]
        if tc.test_data:
            lines += [f"**Test data:** {tc.test_data}", ""]
        lines += [f"**Expected:** {tc.expected_result}", ""]
    if suite.test_code:
        lines += ["## Automated Tests", "", "```", suite.test_code, "```", ""]
    return "\n".join(lines)


EXPORTERS = {"json": to_json, "csv": to_csv, "md": to_markdown}
