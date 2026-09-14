"""The Pydantic model and the published JSON Schema must agree.

Two representations of one contract only stay useful if something checks them
against each other. That is this file.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest
from pydantic import ValidationError

from pure_agent.schemas.task import AgentTask

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas" / "agent-task.schema.json"


@pytest.fixture(scope="module")
def schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_schema_file_is_valid_draft_2020_12(schema):
    jsonschema.Draft202012Validator.check_schema(schema)


def test_valid_task_satisfies_the_json_schema(schema):
    task = AgentTask(task_id="t-1", action="start_instance", instance_id="i-1")
    jsonschema.validate(task.model_dump(), schema)


def test_valid_listing_task_satisfies_the_json_schema(schema):
    jsonschema.validate(AgentTask(task_id="t-1", action="list_instances").model_dump(), schema)


def test_unknown_action_fails_both_representations(schema):
    payload = {"task_id": "t", "action": "delete_everything"}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(payload, schema)
    with pytest.raises(ValidationError):
        AgentTask(**payload)


def test_missing_instance_id_fails_both_representations(schema):
    payload = {"task_id": "t", "action": "start_instance"}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(payload, schema)
    with pytest.raises(ValidationError):
        AgentTask(**payload)


def test_extra_property_fails_the_json_schema(schema):
    payload = {"task_id": "t", "action": "list_instances", "sneaky": 1}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(payload, schema)


def test_action_enum_matches_between_the_two(schema):
    """Drift here is the failure that silently breaks every consumer."""
    from typing import get_args

    from pure_agent.schemas.task import Action

    model_actions = set(get_args(Action))
    schema_actions = set(schema["properties"]["action"]["enum"])
    assert model_actions == schema_actions == {
        "list_instances",
        "start_instance",
        "stop_instance",
        "reboot_instance",
    }
