# Solr to OpenSearch Migration Skill

An **OpenSearch Agent Skill** that helps migrate from [Apache Solr](https://solr.apache.org/) to [OpenSearch](https://opensearch.org/).

## Features

| Capability | Method | Description |
|---|---|---|
| Schema conversion (XML) | `convert_schema_xml()` | Converts a Solr `schema.xml` file to an OpenSearch index mapping |
| Schema conversion (JSON) | `convert_schema_json()` | Converts a Solr Schema API JSON response to an OpenSearch index mapping |
| Query conversion | `convert_query()` | Translates a Solr query string to an OpenSearch Query DSL JSON object |
| Migration checklist | `get_migration_checklist()` | Returns a human-readable migration checklist |
| Field type reference | `get_field_type_mapping_reference()` | Returns a Markdown table of Solr → OpenSearch type mappings |

## Supported Solr → OpenSearch Field Type Mappings

| Solr Field Type | OpenSearch Type |
|---|---|
| `StrField` | `keyword` |
| `TextField` | `text` |
| `IntPointField` / `TrieIntField` | `integer` |
| `LongPointField` / `TrieLongField` | `long` |
| `FloatPointField` / `TrieFloatField` | `float` |
| `DoublePointField` / `TrieDoubleField` | `double` |
| `DatePointField` / `TrieDateField` | `date` |
| `BoolField` | `boolean` |
| `BinaryField` | `binary` |
| `LatLonPointSpatialField` | `geo_point` |
| `SpatialRecursivePrefixTreeFieldType` | `geo_shape` |

## Supported Solr Query Conversions

| Solr Query Pattern | OpenSearch Query DSL |
|---|---|
| `*:*` | `match_all` |
| `field:value` | `match` |
| `field:"phrase value"` | `match_phrase` |
| `field:val*` / `field:*val` | `wildcard` |
| `field:[low TO high]` | `range` (inclusive) |
| `field:{low TO high}` | `range` (exclusive) |
| `field:[* TO high]` / `field:[low TO *]` | open-ended `range` |
| `term1 AND term2` | `bool` / `must` |
| `term1 OR term2` | `bool` / `should` |
| `NOT term` | `bool` / `must_not` |
| `+term1 -term2` | `bool` / `must` + `must_not` |
| bare term | `query_string` (fallback) |

## Installation

```bash
pip install -e ".[dev]"
```

## Usage

```python
import sys
import os
# Add scripts directory to sys.path
sys.path.append(os.path.join(os.getcwd(), "scripts"))

from skill import SolrToOpenSearchMigrationSkill

skill = SolrToOpenSearchMigrationSkill()

# --- Schema conversion ---

# From schema.xml
with open("schema.xml") as f:
    mapping_json = skill.convert_schema_xml(f.read())
print(mapping_json)

# From Solr Schema API JSON (GET /solr/<collection>/schema)
import urllib.request
with urllib.request.urlopen("http://localhost:8983/solr/mycore/schema") as resp:
    schema_api_json = resp.read().decode()
mapping_json = skill.convert_schema_json(schema_api_json)
print(mapping_json)

# --- Query conversion ---
dsl = skill.convert_query("title:opensearch AND category:docs")
print(dsl)

# Range query
dsl = skill.convert_query("price:[10 TO 100]")
print(dsl)

# --- Migration guidance ---
print(skill.get_migration_checklist())
print(skill.get_field_type_mapping_reference())
```

### Example: Convert a schema.xml

Given a Solr `schema.xml`:

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<schema name="products" version="1.6">
  <fieldType name="string" class="solr.StrField" />
  <fieldType name="text_general" class="solr.TextField" />
  <fieldType name="pint" class="solr.IntPointField" />
  <fieldType name="pfloat" class="solr.FloatPointField" />
  <fieldType name="pdate" class="solr.DatePointField" />

  <field name="id"          type="string"       indexed="true"  stored="true" required="true" />
  <field name="name"        type="text_general" indexed="true"  stored="true" />
  <field name="price"       type="pfloat"       indexed="true"  stored="true" />
  <field name="quantity"    type="pint"         indexed="true"  stored="true" />
  <field name="created_at"  type="pdate"        indexed="true"  stored="true" />

  <dynamicField name="*_s" type="string" indexed="true" stored="true" />
</schema>
```

The skill produces:

```json
{
  "mappings": {
    "properties": {
      "id": { "type": "keyword" },
      "name": { "type": "text" },
      "price": { "type": "float" },
      "quantity": { "type": "integer" },
      "created_at": { "type": "date" }
    },
    "dynamic_templates": [
      {
        "dynamic_s": {
          "match": "*_s",
          "match_pattern": "wildcard",
          "mapping": { "type": "keyword" }
        }
      }
    ]
  }
}
```

### Example: Convert a Solr query

```python
skill.convert_query("title:opensearch AND price:[10 TO 100]")
```

```json
{
  "query": {
    "bool": {
      "must": [
        { "match": { "title": "opensearch" } },
        { "range": { "price": { "gte": 10, "lte": 100 } } }
      ]
    }
  }
}
```

## Running the Tests

```bash
cd solr-to-opensearch
pip install -e ".[dev]"
pytest
```

## Project Structure

```
solr-to-opensearch/
├── pyproject.toml
├── requirements-dev.txt
├── README.md
├── SKILL.md
└── scripts/
    ├── __init__.py
    ├── skill.py             # High-level SolrToOpenSearchMigrationSkill class
    ├── schema_converter.py  # Solr schema → OpenSearch mapping converter
    └── query_converter.py   # Solr query syntax → OpenSearch Query DSL converter
```

## License

Apache-2.0
