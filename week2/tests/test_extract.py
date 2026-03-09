import os
import pytest

import json
from types import SimpleNamespace

from ..app.services import extract as extract_module
from ..app.services.extract import extract_action_items, extract_action_items_llm


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


def test_extract_llm_bullets_and_keywords(monkeypatch):
    text = """
    Notes from meeting:
    - Set up database
    todo: Finish the report
    """.strip()

    # Mock ollama.chat to return a valid JSON with action_items
    returned = json.dumps({"action_items": ["Set up database", "Finish the report"]})

    def fake_chat(**kwargs):
        return SimpleNamespace(message=SimpleNamespace(content=returned))

    monkeypatch.setattr(extract_module, "chat", fake_chat)

    items = extract_action_items_llm(text)
    assert items == ["Set up database", "Finish the report"]


def test_extract_llm_empty_input():
    assert extract_action_items_llm("") == []


def test_extract_llm_duplicates(monkeypatch):
    text = "Some text"
    # Model returns duplicates with different casing
    returned = json.dumps({"action_items": ["Do X", "do x", "DO X", "Another"]})

    def fake_chat(**kwargs):
        return SimpleNamespace(message=SimpleNamespace(content=returned))

    monkeypatch.setattr(extract_module, "chat", fake_chat)

    items = extract_action_items_llm(text)
    # Expect deduplication (case-insensitive) preserving first occurrence
    assert items == ["Do X", "Another"]


def test_extract_llm_invalid_json_fallback(monkeypatch):
    text = """
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    """.strip()

    # Mock chat to return invalid/non-JSON content
    def fake_chat(**kwargs):
        return SimpleNamespace(message=SimpleNamespace(content="not a json"))

    monkeypatch.setattr(extract_module, "chat", fake_chat)

    items = extract_action_items_llm(text)
    # Should fall back to the heuristic extractor and include these items
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items
