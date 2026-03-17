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

## Capabilities

### 1. Transport-agnostic Core [P0]

A library with a simple call interface that encapsulates all agentic reasoning. It accepts a message and a session handle and returns a response, with no protocol or deployment assumptions (HTTP, MCP, etc.) baked in.

**Operations:**
- `handle_message(message, session_id)`: Process user input and maintain conversational state.
- `generate_report(session_id)`: Produce a comprehensive migration planning report.

### 2. Pluggable Storage Interface [P0]

A defined storage contract (`load`, `save`, `list_sessions`) allowing each deployment target to supply its own backend (file, database, S3).

- `StorageInterface`: Abstract base class for storage backends.
- `FileStorage`: Default persistent session state implementation.

### 3. Persistent Memory Store [P1]

A session-resumable memory mechanism that preserves conversation state, discovered facts, and migration progress between user sessions.

### 4. Migration Report [P0]

A generated report that gives the user a concrete picture of their migration path, including:
- **Major Milestones**: Identification and suggested sequencing for the migration.
- **Potential Blockers**: Surface unsupported features, plugin dependencies, or architectural mismatches.
- **Implementation Points**: Details where code or configuration changes are required.
- **Front-end Assessment**: Gathers info about the user's front-end integration to assess client-side impact.
- **Cost Estimates**: Infrastructure, effort, and required tooling or licensing changes.

## Migration Workflow

Follow these steps to guide the user through their Solr to OpenSearch migration:

1.  **Initialize Session** — Establish a `session_id` to maintain persistent memory across the migration conversation.
2.  **Request Solr Schema** — If not already provided, prompt the user: *"Please provide your `schema.xml` or Solr Schema API JSON content to begin the schema conversion analysis."*
3.  **Analyze Queries** — Ask the user for representative Solr queries (standard, dismax, edismax) to translate them to OpenSearch Query DSL and identify behavioral differences.
4.  **Assess Cluster & Infrastructure** — Prompt the user for details on their current SolrCloud or standalone topology to provide sizing and resource profiling recommendations.
5.  **Evaluate Front-end Integration** — Ask targeted questions about the user's client-side code: *"What client libraries (e.g., SolrJ, pysolr) or custom front-end integrations are you currently using to communicate with Solr?"*
6.  **Generate Migration Report** — Finalize the process by calling `generate_report` to produce the full migration path, covering milestones, blockers, and cost estimates.

## Instructions

- Always maintain the session context using the `session_id`.
- If a user asks for migration advice but hasn't provided technical details, proactively request the Solr schema or configuration files.
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
