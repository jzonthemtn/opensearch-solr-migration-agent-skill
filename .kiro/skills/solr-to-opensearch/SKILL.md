---
name: solr-to-opensearch
displayName: "Solr to OpenSearch Migration Advisor"
description: >
  Migrate from Apache Solr to OpenSearch. A comprehensive migration advisor that
  handles schema and query translation, sizing recommendations, and 
  incompatibility detection. Includes a transport-agnostic agent core and
  MCP server wrapper.
  Trigger phrases: "migrate from Solr", "convert Solr schema", "translate Solr
  query to OpenSearch", "Solr to OpenSearch migration", "migration advisor".
license: Apache-2.0
compatibility: "Python 3.11+"
metadata:
  author: jzonthemtn
  version: "0.2.0"
keywords: [ "migration", "Solr", "OpenSearch", "schema", "query", "translation", "migration advisor" ]
author: "jzonthemtn"
---

# Apache Solr to OpenSearch Migration Advisor

An agent skill for migrating from Apache Solr to OpenSearch. This skill provides
a transport-agnostic migration advisor that can reason about Solr query behavior,
configuration, and cluster architecture.

## When to Use

Use this skill when:

- A user needs to migrate a Solr collection or SolrCloud deployment to OpenSearch.
- A user wants a comprehensive migration advisor that can handle conversational
  interaction and maintain session context.
- A user has a `schema.xml` or Solr Schema API JSON document and needs an
  equivalent OpenSearch index mapping.
- A user has Solr query strings and needs them translated to OpenSearch Query DSL.
- A user needs a migration report covering milestones, blockers, and cost estimates.

**Trigger phrases:** "migrate from Solr", "convert Solr schema", "translate Solr
query", "Solr to OpenSearch", "migration advisor", "migration report".

## Migration Workflow

Walk the user through each step in order. Do not skip ahead — complete each step before moving to the next.

### Step 1 — Schema Acquisition

Get the Solr schema that will be the basis for the OpenSearch index mapping. There are two paths:

- **Path A — Existing schema:** Ask the user to paste their `schema.xml` or the JSON response from the Solr Schema API (`GET /solr/<collection>/schema`). Call `convert_schema_xml` or `convert_schema_json` accordingly and show the resulting OpenSearch mapping.
- **Path B — No schema yet:** If the user has no existing Solr schema, ask them to provide a sample JSON document that represents the data they plan to index. Infer field names and types from the JSON structure and generate a starter OpenSearch index mapping. Confirm the inferred types with the user before proceeding.

Once a mapping is agreed upon, save it to the session and move to Step 2.

### Step 2 — Schema Review & Incompatibility Analysis

Review the converted or generated mapping for known Solr-to-OpenSearch incompatibilities:

- Flag any `copyField` directives and explain how to replace them with `copy_to` in OpenSearch.
- Identify custom analyzers, tokenizers, or char filters that need to be re-expressed in OpenSearch analysis settings.
- Note any dynamic fields and show the equivalent `dynamic_templates` configuration.
- Highlight fields where the type mapping is ambiguous or lossy (e.g. `text_general` with custom filters).

Present findings as a short list of action items the user needs to resolve.

### Step 3 — Query Translation

Ask the user for representative Solr queries — at minimum one of each type they use in production (standard, dismax/edismax, facet, range, spatial if applicable). For each query:

- Call `convert_query` and show the OpenSearch Query DSL equivalent.
- Note any behavioral differences (e.g. relevance scoring, minimum-should-match semantics, boost handling).
- Flag queries that cannot be automatically translated and explain what manual work is needed.

### Step 4 — Cluster & Infrastructure Assessment

Ask the user about their current deployment topology:

- Standalone Solr or SolrCloud? Number of nodes, shards, and replicas?
- Approximate document count and index size?
- Peak query throughput and indexing rate?

Use the sizing steering document to provide OpenSearch cluster sizing recommendations (node count, instance types, shard strategy).

### Step 5 — Client & Front-end Integration

Ask the user what client-side code talks to Solr today:

- *"What client libraries are you using — SolrJ, pysolr, a custom HTTP client, or something else?"*
- *"Do you have a front-end search UI (e.g. Solr-specific widgets, Velocity templates, or a custom React/Vue app)?"*

Identify which client calls need to change (endpoint URLs, request/response shapes, authentication) and provide concrete before/after examples where possible.

### Step 6 — Migration Report

Call `generate_report` to produce the final report. The report must cover:

- Major milestones and suggested sequencing.
- Blockers surfaced in Steps 2–5.
- Implementation points with enough detail for an engineer to act on.
- Cost estimates for infrastructure, effort, and any required tooling changes.

Present the report to the user and offer to drill into any section.

## Instructions

- Always maintain the session context using the `session_id`.
- Follow the steps in order. If the user jumps ahead, acknowledge their input, store it in the session, and guide them back to complete any skipped steps.
- If a user asks for migration advice but hasn't provided technical details, proactively request the Solr schema or a sample JSON document (Step 1).
- Use the steering documents (Query Translation, Index Design, Sizing, Incompatibilities) to inform all reasoning.

### Usage

#### Library Usage
```python
import sys
import os
# Add scripts directory to sys.path
sys.path.append(os.path.join(os.getcwd(), ".kiro/skills/solr-to-opensearch/scripts"))

from skill import SolrToOpenSearchMigrationSkill

# Initialize advisor
skill = SolrToOpenSearchMigrationSkill()

# Handle conversational message
session_id = "user-123"
response = skill.handle_message("Help me migrate my Solr schema: <schema>...</schema>", session_id)
print(response)

# Generate final report
report = skill.generate_report(session_id)
print(report)
```

#### MCP Server Usage
Install dependencies and run the MCP server over stdio:
```bash
pip install -e ".kiro/skills/solr-to-opensearch[mcp]"
python .kiro/skills/solr-to-opensearch/scripts/mcp_server.py
```

Or configure it in your MCP client (e.g. `.kiro/settings/mcp.json`):
```json
{
  "mcpServers": {
    "solr-to-opensearch": {
      "command": "python3",
      "args": [".kiro/skills/solr-to-opensearch/scripts/mcp_server.py"],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## Reference Data

### Field Type Mapping Reference
| Solr Field Type | OpenSearch Type |
|---|---|
| TextField | text |
| StrField | keyword |
| IntPointField / TrieIntField | integer |
| LongPointField / TrieLongField | long |
| FloatPointField / TrieFloatField | float |
| DoublePointField / TrieDoubleField | double |
| DatePointField / TrieDateField | date |
| BoolField | boolean |
| BinaryField | binary |
| LatLonPointSpatialField | geo_point |
| SpatialRecursivePrefixTreeFieldType | geo_shape |
