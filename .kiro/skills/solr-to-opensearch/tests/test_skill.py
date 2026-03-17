"""Tests for skill.py"""
import sys
import os
import json
import pytest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from skill import SolrToOpenSearchMigrationSkill
from storage import StorageInterface


class InMemoryStorage(StorageInterface):
    def __init__(self):
        self._store = {}

    def save(self, session_id, data):
        self._store[session_id] = data

    def load(self, session_id):
        return self._store.get(session_id)

    def list_sessions(self):
        return list(self._store.keys())


@pytest.fixture
def skill():
    return SolrToOpenSearchMigrationSkill(storage=InMemoryStorage())


SIMPLE_SCHEMA_XML = """<schema name="test" version="1.6">
  <fieldType name="string" class="solr.StrField"/>
  <field name="id" type="string" indexed="true" stored="true"/>
  <field name="title" type="string" indexed="true" stored="true"/>
</schema>"""


# --- convert_schema_xml ---

def test_convert_schema_xml_returns_json(skill):
    result = skill.convert_schema_xml(SIMPLE_SCHEMA_XML)
    parsed = json.loads(result)
    assert "mappings" in parsed
    assert parsed["mappings"]["properties"]["id"]["type"] == "keyword"


def test_convert_schema_xml_invalid_raises(skill):
    with pytest.raises(ValueError):
        skill.convert_schema_xml("not xml")


# --- convert_schema_json ---

def test_convert_schema_json_returns_json(skill):
    schema_json = json.dumps({
        "schema": {
            "fieldTypes": [{"name": "string", "class": "solr.StrField"}],
            "fields": [{"name": "title", "type": "string"}],
        }
    })
    result = skill.convert_schema_json(schema_json)
    parsed = json.loads(result)
    assert parsed["mappings"]["properties"]["title"]["type"] == "keyword"


def test_convert_schema_json_invalid_raises(skill):
    with pytest.raises(ValueError):
        skill.convert_schema_json("{bad}")


# --- convert_query ---

def test_convert_query_match_all(skill):
    result = skill.convert_query("*:*")
    assert json.loads(result) == {"query": {"match_all": {}}}


def test_convert_query_field_value(skill):
    result = skill.convert_query("title:opensearch")
    parsed = json.loads(result)
    assert parsed["query"]["match"]["title"] == "opensearch"


def test_convert_query_empty_raises(skill):
    with pytest.raises(ValueError):
        skill.convert_query("")


# --- get_migration_checklist ---

def test_get_migration_checklist_contains_sections(skill):
    checklist = skill.get_migration_checklist()
    assert "PREPARATION" in checklist
    assert "SCHEMA" in checklist
    assert "QUERY MIGRATION" in checklist
    assert "CUTOVER" in checklist


# --- get_field_type_mapping_reference ---

def test_get_field_type_mapping_reference_is_markdown_table(skill):
    ref = skill.get_field_type_mapping_reference()
    assert "| Solr Field Type | OpenSearch Type |" in ref
    assert "text" in ref
    assert "keyword" in ref


# --- handle_message ---

def test_handle_message_schema_conversion(skill):
    msg = f"Please convert this schema: {SIMPLE_SCHEMA_XML}"
    response = skill.handle_message(msg, "s1")
    assert "mappings" in response or "OpenSearch" in response


def test_handle_message_query_translation(skill):
    response = skill.handle_message("translate query: title:opensearch", "s2")
    assert "match" in response or "OpenSearch" in response


def test_handle_message_checklist(skill):
    response = skill.handle_message("show me the checklist", "s3")
    assert "PREPARATION" in response or "checklist" in response.lower()


def test_handle_message_report(skill):
    response = skill.handle_message("generate report", "s4")
    assert "Migration Report" in response


def test_handle_message_unknown_returns_greeting(skill):
    response = skill.handle_message("hello there", "s5")
    assert len(response) > 0


def test_handle_message_persists_session(skill):
    skill.handle_message("hello", "persist-test")
    storage = skill._storage
    session = storage.load("persist-test")
    assert session is not None
    assert len(session["history"]) == 1


# --- generate_report ---

def test_generate_report_no_session(skill):
    report = skill.generate_report("empty-session")
    assert "Migration Report" in report


def test_generate_report_flags_missing_schema(skill):
    report = skill.generate_report("no-schema-session")
    assert "Schema not yet analyzed" in report


def test_generate_report_after_schema_migration(skill):
    skill.handle_message(f"convert: {SIMPLE_SCHEMA_XML}", "schema-session")
    # Manually mark schema as migrated
    data = skill._storage.load("schema-session") or {}
    data.setdefault("facts", {})["schema_migrated"] = True
    skill._storage.save("schema-session", data)
    report = skill.generate_report("schema-session")
    assert "Schema not yet analyzed" not in report
