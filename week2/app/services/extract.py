from __future__ import annotations

import os
import re
from typing import List
import json
from typing import Any
from ollama import chat
from dotenv import load_dotenv

load_dotenv()

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters


def extract_action_items_llm(text: str) -> list[str]:
    """Extract action items using the Ollama LLM with a JSON-schema structured output.

    Returns a list of unique action item strings. Handles empty input, invalid JSON
    from the model by falling back to the heuristic `extract_action_items`, and
    removes duplicates while preserving order.
    """
    # Handle empty input early
    if not text or not text.strip():
        return []

    system_prompt = (
        "You are an automated extractor. Parse the user's input and return a JSON object\n"
        "with a single field `action_items` which is an array of short strings, each an\n"
        "actionable item. Output ONLY valid JSON that matches the provided schema."
    )

    # Define a JSON schema for structured output
    format_spec = {
        "type": "json_schema",
        "json_schema": {
            "name": "ActionItems",
            "schema": {
                "type": "object",
                "properties": {
                    "action_items": {
                        "type": "array",
                        "items": {"type": "string"},
                    }
                },
                "required": ["action_items"],
            },
        },
    }

    try:
        response = chat(
            model=os.environ.get("OLLAMA_MODEL", "llama3.1:8b"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            format=format_spec,
            options={"temperature": 0.0},
        )
    except Exception:
        # If the API call fails for any reason, fall back to the heuristic extractor
        return extract_action_items(text)

    # Safely obtain the model's text output
    content = ""
    try:
        # repository usage uses response.message.content elsewhere
        content = getattr(response, "message", None)
        if content is not None:
            content = getattr(content, "content", "")
        if not isinstance(content, str):
            content = str(content or "")
    except Exception:
        content = ""

    if not content:
        return extract_action_items(text)

    # Try to parse JSON; be resilient to code fences or minor wrapper text
    def _try_load_json(s: str):
        s = s.strip()
        # strip code fences if present
        if s.startswith("```") and s.endswith("```"):
            s = s.strip("`")
            if s.lower().startswith("json\n"):
                s = s[5:]
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            return None

    parsed = _try_load_json(content)
    if parsed is None:
        # Invalid JSON -> fallback to heuristic extractor
        return extract_action_items(text)

    # Extract action_items field, validating type
    items = parsed.get("action_items") if isinstance(parsed, dict) else None
    if not isinstance(items, list):
        return extract_action_items(text)

    # Coerce items to strings and deduplicate while preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for it in items:
        if it is None:
            continue
        s = str(it).strip()
        if not s:
            continue
        key = s.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(s)

    return unique
