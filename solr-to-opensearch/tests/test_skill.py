"""Tests for SolrToOpenSearchMigrationSkill."""

import json
import pytest

from solr_to_opensearch.skill import SolrToOpenSearchMigrationSkill


@pytest.fixture()
def skill() -> SolrToOpenSearchMigrationSkill:
    return SolrToOpenSearchMigrationSkill()


SAMPLE_SCHEMA_XML = """<?xml version="1.0" encoding="UTF-8" ?>
<schema name="sample" version="1.6">
  <fieldType name="string" class="solr.StrField" />
  <fieldType name="text_general" class="solr.TextField" />
  <fieldType name="int" class="solr.IntPointField" />

  <field name="id" type="string" indexed="true" stored="true" />
  <field name="title" type="text_general" indexed="true" stored="true" />
  <field name="count" type="int" indexed="true" stored="true" />
</schema>
"""

SAMPLE_SCHEMA_API_JSON = json.dumps({
    "schema": {
        "fieldTypes": [
            {"name": "string", "class": "solr.StrField"},
            {"name": "text_general", "class": "solr.TextField"},
        ],
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "body", "type": "text_general"},
        ],
    }
})


# ---------------------------------------------------------------------------
# convert_schema_xml
# ---------------------------------------------------------------------------

def test_convert_schema_xml_returns_valid_json(skill):
    result = skill.convert_schema_xml(SAMPLE_SCHEMA_XML)
    data = json.loads(result)
    assert "mappings" in data
    assert "properties" in data["mappings"]


def test_convert_schema_xml_field_types(skill):
    result = json.loads(skill.convert_schema_xml(SAMPLE_SCHEMA_XML))
    props = result["mappings"]["properties"]
    assert props["id"]["type"] == "keyword"
    assert props["title"]["type"] == "text"
    assert props["count"]["type"] == "integer"


def test_convert_schema_xml_indent(skill):
    result_2 = skill.convert_schema_xml(SAMPLE_SCHEMA_XML, indent=2)
    result_4 = skill.convert_schema_xml(SAMPLE_SCHEMA_XML, indent=4)
    # Both should be valid JSON with the same data.
    assert json.loads(result_2) == json.loads(result_4)
    # 4-space indent should be longer.
    assert len(result_4) > len(result_2)


# ---------------------------------------------------------------------------
# convert_schema_json
# ---------------------------------------------------------------------------

def test_convert_schema_json_returns_valid_json(skill):
    result = skill.convert_schema_json(SAMPLE_SCHEMA_API_JSON)
    data = json.loads(result)
    assert "mappings" in data


def test_convert_schema_json_field_types(skill):
    result = json.loads(skill.convert_schema_json(SAMPLE_SCHEMA_API_JSON))
    props = result["mappings"]["properties"]
    assert props["id"]["type"] == "keyword"
    assert props["body"]["type"] == "text"


# ---------------------------------------------------------------------------
# convert_query
# ---------------------------------------------------------------------------

def test_convert_query_returns_valid_json(skill):
    result = skill.convert_query("title:opensearch")
    data = json.loads(result)
    assert "query" in data


def test_convert_query_match_all(skill):
    result = json.loads(skill.convert_query("*:*"))
    assert result["query"] == {"match_all": {}}


def test_convert_query_field_value(skill):
    result = json.loads(skill.convert_query("category:docs"))
    assert result["query"] == {"match": {"category": "docs"}}


def test_convert_query_range(skill):
    result = json.loads(skill.convert_query("price:[10 TO 50]"))
    assert result["query"] == {"range": {"price": {"gte": 10, "lte": 50}}}


def test_convert_query_boolean_and(skill):
    result = json.loads(skill.convert_query("title:search AND category:docs"))
    assert "bool" in result["query"]
    assert "must" in result["query"]["bool"]


# ---------------------------------------------------------------------------
# get_migration_checklist
# ---------------------------------------------------------------------------

def test_get_migration_checklist_is_non_empty_string(skill):
    result = skill.get_migration_checklist()
    assert isinstance(result, str)
    assert len(result) > 100


def test_get_migration_checklist_contains_key_sections(skill):
    checklist = skill.get_migration_checklist()
    assert "PREPARATION" in checklist
    assert "SCHEMA" in checklist
    assert "QUERY" in checklist
    assert "DATA MIGRATION" in checklist
    assert "TESTING" in checklist
    assert "CUTOVER" in checklist


# ---------------------------------------------------------------------------
# get_field_type_mapping_reference
# ---------------------------------------------------------------------------

def test_get_field_type_mapping_reference_is_markdown_table(skill):
    result = skill.get_field_type_mapping_reference()
    assert "| Solr Field Type | OpenSearch Type |" in result
    assert "|---|---|" in result


def test_get_field_type_mapping_reference_contains_common_types(skill):
    result = skill.get_field_type_mapping_reference()
    assert "TextField" in result
    assert "StrField" in result
    assert "IntPointField" in result
