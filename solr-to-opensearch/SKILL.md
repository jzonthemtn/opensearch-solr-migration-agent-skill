---
name: solr-to-opensearch
description: >
  Migrate from Apache Solr to OpenSearch. Converts Solr schema definitions
  (schema.xml or Solr Schema API JSON) into OpenSearch index mappings, translates
  Solr query strings into OpenSearch Query DSL, and provides a step-by-step
  migration checklist plus a field-type reference table. Use when a user needs
  to migrate an existing Solr deployment to OpenSearch, convert a Solr schema to
  an index mapping, or translate Solr queries to OpenSearch Query DSL.
  Trigger phrases: "migrate from Solr", "convert Solr schema", "translate Solr
  query to OpenSearch", "Solr to OpenSearch migration".
license: Apache-2.0
compatibility: "Python 3.11+"
metadata:
  author: jzonthemtn
  version: "0.1.0"
---

# solr-to-opensearch

An agent skill for migrating from Apache Solr to OpenSearch. Converts schemas,
translates queries, and provides comprehensive migration guidance.

## When to Use

Use this skill when:

- A user needs to migrate a Solr collection or SolrCloud deployment to OpenSearch.
- A user has a `schema.xml` or Solr Schema API JSON document and needs an
  equivalent OpenSearch index mapping.
- A user has Solr query strings (`q` parameter values) and needs them translated
  to OpenSearch Query DSL.
- A user wants a checklist of tasks to complete a Solr → OpenSearch migration.
- A user wants a reference table of Solr field types and their OpenSearch
  equivalents.

**Trigger phrases:** "migrate from Solr", "convert Solr schema", "translate Solr
query", "Solr to OpenSearch", "move from Solr to OpenSearch".

## Operations

### 1. Convert a Solr Schema XML to an OpenSearch Mapping

User provides the content of a Solr `schema.xml` file and requests an equivalent
OpenSearch index mapping.

**Examples:**
- "Convert my schema.xml to an OpenSearch mapping"
- "Here is my Solr schema, give me the OpenSearch equivalent"
- "Translate this schema.xml for use with OpenSearch"

### 2. Convert a Solr Schema API JSON to an OpenSearch Mapping

User provides the JSON returned by the Solr Schema API
(`GET /solr/<collection>/schema`) and requests an equivalent OpenSearch mapping.

**Examples:**
- "Convert this Solr Schema API response to an OpenSearch mapping"
- "I exported my schema as JSON from Solr, convert it to OpenSearch format"

### 3. Translate a Solr Query to OpenSearch Query DSL

User provides a Solr query string and requests the equivalent OpenSearch Query
DSL.

**Examples:**
- "Translate this Solr query to OpenSearch: title:opensearch AND price:[10 TO 100]"
- "Convert my Solr q parameter to OpenSearch Query DSL"
- "What is the OpenSearch equivalent of category:docs AND NOT status:archived?"

### 4. Get a Migration Checklist

User asks for a checklist of migration tasks.

**Examples:**
- "Give me a Solr to OpenSearch migration checklist"
- "What steps do I need to take to migrate from Solr?"

### 5. Get a Field Type Mapping Reference

User asks how Solr field types map to OpenSearch types.

**Examples:**
- "How do Solr field types map to OpenSearch?"
- "What is the OpenSearch equivalent of solr.StrField?"

## Workflow

1. **Identify the operation** — Determine from the user's request which of the
   five operations above is needed.
2. **Gather inputs** — For schema conversion, obtain the schema content (XML
   string or JSON string). For query translation, obtain the Solr query string.
3. **Invoke the skill** — Call the appropriate method of
   `SolrToOpenSearchMigrationSkill`.
4. **Present the output** — Return the JSON mapping, Query DSL JSON, or plain-text
   checklist/table to the user.
5. **Follow up** — Offer to convert additional queries, address edge cases, or
   explain individual mapping decisions.

## Instructions

### Schema Conversion

```python
from solr_to_opensearch import SolrToOpenSearchMigrationSkill

skill = SolrToOpenSearchMigrationSkill()

# From schema.xml
with open("schema.xml") as f:
    mapping_json = skill.convert_schema_xml(f.read())
print(mapping_json)

# From Solr Schema API JSON (GET /solr/<collection>/schema)
with open("solr_schema_api.json") as f:
    mapping_json = skill.convert_schema_json(f.read())
print(mapping_json)
```

### Query Translation

```python
# Simple field query
dsl = skill.convert_query("title:opensearch")
# → {"query": {"match": {"title": "opensearch"}}}

# Boolean AND
dsl = skill.convert_query("title:search AND category:docs")
# → {"query": {"bool": {"must": [...]}}}

# Range
dsl = skill.convert_query("price:[10 TO 100]")
# → {"query": {"range": {"price": {"gte": 10, "lte": 100}}}}

# Phrase
dsl = skill.convert_query('description:"full text search"')
# → {"query": {"match_phrase": {"description": "full text search"}}}

# match_all
dsl = skill.convert_query("*:*")
# → {"query": {"match_all": {}}}
```

### Migration Checklist

```python
print(skill.get_migration_checklist())
```

### Field Type Reference

```python
print(skill.get_field_type_mapping_reference())
```

## Supported Conversions

### Solr Field Types → OpenSearch Types

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

### Solr Query Patterns → OpenSearch Query DSL

| Solr Query Pattern | OpenSearch Query Type |
|---|---|
| `*:*` | `match_all` |
| `field:value` | `match` |
| `field:"phrase value"` | `match_phrase` |
| `field:val*` / `field:*val` | `wildcard` |
| `field:[low TO high]` | `range` (inclusive `gte`/`lte`) |
| `field:{low TO high}` | `range` (exclusive `gt`/`lt`) |
| `field:[* TO high]` / `field:[low TO *]` | open-ended `range` |
| `term1 AND term2` | `bool` / `must` |
| `term1 OR term2` | `bool` / `should` |
| `NOT term` | `bool` / `must_not` |
| `+required -prohibited` | `bool` / `must` + `must_not` |
| bare term | `query_string` (fallback) |

### Dynamic Field Handling

Solr `<dynamicField>` entries (e.g. `*_i`, `*_s`) are converted to OpenSearch
`dynamic_templates` in the index mapping.

### Field Attribute Propagation

| Solr Attribute | OpenSearch Mapping Property |
|---|---|
| `stored="false"` | `"store": false` |
| `indexed="false"` | `"index": false` |
| `docValues="true"` | `"doc_values": true` |

## Limitations

- Nested parenthesis grouping in complex Solr queries falls back to a
  `query_string` clause so that no information is lost.
- Boost values (`^n`) are stripped; boost-aware equivalents such as
  `function_score` must be added manually.
- Fuzzy (`~`) and proximity operators fall back to `query_string`.
- eDismax-specific parameters (`qf`, `pf`, `mm`, `boost`) are not converted;
  the corresponding OpenSearch `multi_match` / `function_score` queries must be
  constructed manually.
- Custom Solr analyzers are not converted automatically; the user must translate
  them to OpenSearch analysis settings.

## Examples

### Example 1: Schema XML Conversion

**Input (`schema.xml`):**

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<schema name="products" version="1.6">
  <fieldType name="string" class="solr.StrField" />
  <fieldType name="text_general" class="solr.TextField" />
  <fieldType name="pfloat" class="solr.FloatPointField" />
  <fieldType name="pint" class="solr.IntPointField" />
  <fieldType name="pdate" class="solr.DatePointField" />

  <field name="id"         type="string"       indexed="true" stored="true" />
  <field name="name"       type="text_general" indexed="true" stored="true" />
  <field name="price"      type="pfloat"       indexed="true" stored="true" />
  <field name="quantity"   type="pint"         indexed="true" stored="true" />
  <field name="created_at" type="pdate"        indexed="true" stored="true" />

  <dynamicField name="*_s" type="string" indexed="true" stored="true" />
</schema>
```

**Output (OpenSearch index mapping):**

```json
{
  "mappings": {
    "properties": {
      "id":         { "type": "keyword" },
      "name":       { "type": "text" },
      "price":      { "type": "float" },
      "quantity":   { "type": "integer" },
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

### Example 2: Query Translation

**Input (Solr query):** `title:opensearch AND price:[10 TO 100]`

**Output (OpenSearch Query DSL):**

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

### Example 3: Full Migration Workflow

```python
from solr_to_opensearch import SolrToOpenSearchMigrationSkill

skill = SolrToOpenSearchMigrationSkill()

# Step 1: Convert the schema
with open("schema.xml") as f:
    mapping_json = skill.convert_schema_xml(f.read())

# Step 2: Create the OpenSearch index (using opensearch-py)
from opensearchpy import OpenSearch
client = OpenSearch("https://localhost:9200")
client.indices.create(index="my_index", body=mapping_json)

# Step 3: Translate queries used in the application
queries = [
    "status:active AND category:electronics",
    "price:[50 TO 500]",
    'description:"free shipping"',
]
for q in queries:
    print(skill.convert_query(q))
```

## Tools

- **Python 3.11+** standard library only (`xml.etree.ElementTree`, `json`, `re`)
- No third-party runtime dependencies

## Installation

```bash
cd solr-to-opensearch
pip install -e .        # runtime only
pip install -e ".[dev]" # include pytest for running tests
```

## Testing

```bash
cd solr-to-opensearch
pip install -e ".[dev]"
pytest
```

All 50 tests cover:
- `SchemaConverter`: XML and JSON schema conversion, field types, attributes,
  dynamic fields, error handling.
- `QueryConverter`: all supported query patterns, boolean operators, boost
  stripping, error handling.
- `SolrToOpenSearchMigrationSkill`: end-to-end facade, JSON output, checklist
  and reference table content.

## References

- [OpenSearch Index API](https://opensearch.org/docs/latest/api-reference/index-apis/)
- [OpenSearch Field Types / Mappings](https://opensearch.org/docs/latest/field-types/)
- [OpenSearch Query DSL](https://opensearch.org/docs/latest/query-dsl/)
- [OpenSearch Aggregations](https://opensearch.org/docs/latest/aggregations/) (for Solr facets)
- [OpenSearch Analysis](https://opensearch.org/docs/latest/analyzers/) (for custom analyzers)
- [OpenSearch Migration Guide](https://opensearch.org/docs/latest/migration-guide/)
- [Apache Solr Reference Guide](https://solr.apache.org/guide/)

## Troubleshooting

### Schema conversion produces `"type": "keyword"` for all fields

**Cause:** The field type name in the `<field type="...">` attribute does not
match any `<fieldType name="...">` entry in the schema.

**Fix:** Ensure the `schema.xml` being passed includes both `<fieldType>`
definitions and `<field>` declarations. If using the Solr Schema API JSON format,
check that the `fieldTypes` array is populated.

### Query conversion returns a `query_string` fallback

**Cause:** The query contains unsupported syntax (fuzzy `~`, proximity, nested
boolean groups).

**Fix:** Review the [Limitations](#limitations) section. For complex queries,
construct the OpenSearch Query DSL manually using the `query_string` output as a
starting point.

### `ValueError: Invalid XML` or `ValueError: Expected root element <schema>`

**Cause:** The input to `convert_schema_xml()` is not a valid Solr `schema.xml`.

**Fix:** Confirm the input is the full XML content of a Solr `schema.xml` file,
not a partial snippet or a different file format.
