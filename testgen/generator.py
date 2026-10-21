import anthropic

from .models import TestSuite

MODEL = "claude-opus-5-5"

SYSTEM_PROMPT = """You are a senior QA engineer. Given a feature description, user story, \
API spec, or source code, design a test suite that a team could execute as-is.

- Cover the categories the user asks for. Favour cases that would catch real bugs: \
boundaries, invalid input, state transitions, error handling, and permissions.
- Steps are concrete actions; expected results are observable and checkable.
- Use realistic test data with actual values, not placeholders.
- Don't pad the suite with near-duplicates. If the input is ambiguous, state your \
assumption in `assumptions` rather than inventing requirements silently.
- Fill `test_code` only when the user asks for an automation framework; the code must \
be complete and runnable, implement the listed cases, and reference their IDs in comments. \
Otherwise leave it as an empty string."""


class GenerationError(Exception):
    pass


def build_prompt(source: str, categories: list[str], count: int, framework: str | None) -> str:
    parts = [
        f"Generate about {count} test cases.",
        f"Categories to cover: {', '.join(categories)}.",
        f"Also write automated tests using: {framework}." if framework else "Do not write automation code.",
        "",
        "<input>",
        source.strip(),
        "</input>",
    ]
    return "\n".join(parts)


def generate_tests(
    source: str,
    categories: list[str] | None = None,
    count: int = 10,
    framework: str | None = None,
    effort: str = "medium",
    client: anthropic.Anthropic | None = None,
) -> TestSuite:
    if not source.strip():
        raise GenerationError("Input is empty - provide a requirement, user story, or code.")
    categories = categories or ["positive", "negative", "edge", "boundary"]
    client = client or anthropic.Anthropic()

    try:
        with client.beta.messages.stream(
            model=MODEL,
            max_tokens=64000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": build_prompt(source, categories, count, framework)}],
            output_format=TestSuite,
            output_config={"effort": effort},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        ) as stream:
            message = stream.get_final_message()
    except anthropic.AuthenticationError as e:
        raise GenerationError("Authentication failed - set ANTHROPIC_API_KEY or run `ant auth login`.") from e
    except anthropic.RateLimitError as e:
        raise GenerationError("Rate limited by the API - wait a moment and retry.") from e
    except anthropic.APIStatusError as e:
        raise GenerationError(f"API error {e.status_code}: {e.message}") from e
    except anthropic.APIConnectionError as e:
        raise GenerationError("Could not reach the Anthropic API - check your network.") from e

    if message.stop_reason == "refusal":
        raise GenerationError("The model declined this request.")
    if message.stop_reason == "max_tokens":
        raise GenerationError("Output was cut off - request fewer test cases.")

    text = "".join(b.text for b in message.content if b.type == "text")
    return TestSuite.model_validate_json(text)
