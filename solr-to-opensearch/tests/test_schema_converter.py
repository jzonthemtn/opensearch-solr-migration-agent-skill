"""Tests for SchemaConverter."""

import json
import pytest

from solr_to_opensearch.schema_converter import SchemaConverter


@pytest.fixture()
def converter() -> SchemaConverter:
    return SchemaConverter()


# ---------------------------------------------------------------------------
# Minimal schema XML
# ---------------------------------------------------------------------------

MINIMAL_SCHEMA_XML = """<?xml version="1.0" encoding="UTF-8" ?>
<schema name="minimal" version="1.6">
  <fieldType name="string" class="solr.StrField" />
  <fieldType name="text_general" class="solr.TextField" />
  <fieldType name="int" class="solr.IntPointField" />
  <fieldType name="long" class="solr.LongPointField" />
  <fieldType name="float" class="solr.FloatPointField" />
  <fieldType name="double" class="solr.DoublePointField" />
  <fieldType name="date" class="solr.DatePointField" />
  <fieldType name="boolean" class="solr.BoolField" />

  <field name="id" type="string" indexed="true" stored="true" required="true" />
  <field name="title" type="text_general" indexed="true" stored="true" />
  <field name="price" type="float" indexed="true" stored="true" />
  <field name="quantity" type="int" indexed="true" stored="true" />
  <field name="created" type="date" indexed="true" stored="true" />
  <field name="active" type="boolean" indexed="true" stored="true" />
</schema>
"""


def test_convert_xml_returns_mapping_key(converter):
    result = converter.convert_xml(MINIMAL_SCHEMA_XML)
    assert "mappings" in result
    assert "properties" in result["mappings"]


def test_convert_xml_field_types(converter):
    result = converter.convert_xml(MINIMAL_SCHEMA_XML)
    props = result["mappings"]["properties"]

    assert props["id"]["type"] == "keyword"
    assert props["title"]["type"] == "text"
    assert props["price"]["type"] == "float"
    assert props["quantity"]["type"] == "integer"
    assert props["created"]["type"] == "date"
    assert props["active"]["type"] == "boolean"


def test_convert_xml_skips_internal_fields(converter):
    schema_with_version = MINIMAL_SCHEMA_XML.replace(
        "<field name=\"id\"",
        "<field name=\"_version_\" type=\"long\" indexed=\"true\" stored=\"true\" />\n  <field name=\"id\"",
    )
    result = converter.convert_xml(schema_with_version)
    assert "_version_" not in result["mappings"]["properties"]


def test_convert_xml_not_stored_sets_store_false(converter):
    schema = """<?xml version="1.0" ?>
<schema name="test" version="1.6">
  <fieldType name="string" class="solr.StrField" />
  <field name="hidden" type="string" indexed="true" stored="false" />
</schema>"""
    result = converter.convert_xml(schema)
    assert result["mappings"]["properties"]["hidden"].get("store") is False


def test_convert_xml_not_indexed_sets_index_false(converter):
    schema = """<?xml version="1.0" ?>
<schema name="test" version="1.6">
  <fieldType name="text_general" class="solr.TextField" />
  <field name="body" type="text_general" indexed="false" stored="true" />
</schema>"""
    result = converter.convert_xml(schema)
    assert result["mappings"]["properties"]["body"].get("index") is False


def test_convert_xml_dynamic_fields(converter):
    schema = """<?xml version="1.0" ?>
<schema name="test" version="1.6">
  <fieldType name="string" class="solr.StrField" />
  <fieldType name="int" class="solr.IntPointField" />
  <field name="id" type="string" />
  <dynamicField name="*_i" type="int" indexed="true" stored="true" />
</schema>"""
    result = converter.convert_xml(schema)
    assert "dynamic_templates" in result["mappings"]
    template = result["mappings"]["dynamic_templates"][0]
    assert "dynamic_i" in template
    assert template["dynamic_i"]["mapping"]["type"] == "integer"


def test_convert_xml_invalid_xml_raises(converter):
    with pytest.raises(ValueError, match="Invalid XML"):
        converter.convert_xml("not xml at all")


def test_convert_xml_wrong_root_raises(converter):
    with pytest.raises(ValueError, match="Expected root element"):
        converter.convert_xml("<notschema />")


# ---------------------------------------------------------------------------
# Schema API JSON
# ---------------------------------------------------------------------------

SCHEMA_API_JSON = json.dumps({
    "schema": {
        "name": "example",
        "fieldTypes": [
            {"name": "string", "class": "solr.StrField"},
            {"name": "text_general", "class": "solr.TextField"},
            {"name": "plong", "class": "solr.LongPointField"},
            {"name": "location", "class": "solr.LatLonPointSpatialField"},
        ],
        "fields": [
            {"name": "id", "type": "string", "indexed": True, "stored": True},
            {"name": "description", "type": "text_general", "indexed": True, "stored": True},
            {"name": "views", "type": "plong", "indexed": True, "stored": True, "docValues": True},
            {"name": "latlon", "type": "location", "indexed": True, "stored": True},
        ],
        "dynamicFields": [
            {"name": "*_s", "type": "string", "indexed": True, "stored": True},
        ],
    }
})


def test_convert_json_returns_mapping_key(converter):
    result = converter.convert_json(SCHEMA_API_JSON)
    assert "mappings" in result
    assert "properties" in result["mappings"]


def test_convert_json_field_types(converter):
    result = converter.convert_json(SCHEMA_API_JSON)
    props = result["mappings"]["properties"]

    assert props["id"]["type"] == "keyword"
    assert props["description"]["type"] == "text"
    assert props["views"]["type"] == "long"
    assert props["latlon"]["type"] == "geo_point"


def test_convert_json_doc_values(converter):
    result = converter.convert_json(SCHEMA_API_JSON)
    assert result["mappings"]["properties"]["views"].get("doc_values") is True


def test_convert_json_dynamic_fields(converter):
    result = converter.convert_json(SCHEMA_API_JSON)
    assert "dynamic_templates" in result["mappings"]
    template = result["mappings"]["dynamic_templates"][0]
    assert "dynamic_s" in template
    assert template["dynamic_s"]["mapping"]["type"] == "keyword"


def test_convert_json_invalid_json_raises(converter):
    with pytest.raises(ValueError, match="Invalid JSON"):
        converter.convert_json("{invalid json}")


def test_convert_json_without_schema_wrapper(converter):
    """Schema API JSON without the outer 'schema' key should also work."""
    raw = {
        "fieldTypes": [{"name": "string", "class": "solr.StrField"}],
        "fields": [{"name": "title", "type": "string"}],
    }
    result = converter.convert_json(json.dumps(raw))
    assert result["mappings"]["properties"]["title"]["type"] == "keyword"
