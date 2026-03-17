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

Once a mapping is agreed upon, save it to the session.

**Optional — Create the index in OpenSearch:** After presenting the mapping, ask the user:
*"Would you like me to create this index in OpenSearch now?"*
Only call `create_opensearch_index` if the user explicitly agrees. Pass the agreed-upon index name and the mapping JSON. If the user declines or does not respond affirmatively, skip this step and move on. Inform the user that `OPENSEARCH_URL`, `OPENSEARCH_USER`, and `OPENSEARCH_PASSWORD` environment variables can be set to point to their cluster (defaults to `http://localhost:9200`).

Move to Step 2.

### Step 2 — Schema Review & Incompatibility Analysis

This step is the primary incompatibility gate. Treat every finding as a potential blocker and be thorough — missed incompatibilities discovered late in a migration are expensive to fix.

Systematically check the converted mapping against every category in the **Incompatibility Reference** section below. For each issue found:

1. Classify it as one of: **Breaking** (will cause data loss or index failure), **Behavioral** (works but produces different results), or **Unsupported** (feature has no OpenSearch equivalent).
2. Record it in the session under `facts.incompatibilities` as a list of objects with keys `category`, `severity`, `description`, and `recommendation`.
3. Present it to the user immediately with a clear explanation and the recommended resolution.

Specific checks to perform on the schema:

- **copyField** — flag every `<copyField>` directive; explain replacement with `copy_to` on the source field definition.
- **Field type gaps** — flag `solr.ICUCollationField`, `solr.EnumField`, `solr.ExternalFileField`, `solr.PreAnalyzedField`, and `solr.SortableTextField` as unsupported or requiring manual workarounds.
- **Custom analyzers** — identify any `<analyzer>`, `<tokenizer>`, or `<filter>` referencing a non-standard class. Check whether an equivalent exists in OpenSearch's built-in analysis chain; flag those that do not.
- **Dynamic fields** — note that OpenSearch `dynamic_templates` match on field name patterns or data types, not Solr's glob syntax; verify the converted templates preserve the intended behavior.
- **Stored vs. source** — Solr stores fields individually; OpenSearch stores the original `_source` document. Fields marked `stored="true"` but `indexed="false"` in Solr may behave differently under `_source` filtering.
- **DocValues** — Solr requires explicit `docValues="true"` for sorting/faceting on most field types; in OpenSearch, `doc_values` is enabled by default for most types. Flag any field where the Solr schema explicitly disables docValues, as the OpenSearch default may change behavior.
- **Nested / child documents** — Solr block join (`{!parent}`, `{!child}`) has no direct equivalent; flag and recommend OpenSearch [nested objects](https://opensearch.org/docs/latest/field-types/supported-field-types/nested/) or [join field type](https://opensearch.org/docs/latest/field-types/supported-field-types/join/).
- **Trie field types** — `TrieIntField`, `TrieLongField`, etc. are deprecated in Solr 7+ and have no equivalent in OpenSearch; confirm the user is migrating to the Point field equivalents.

Present all findings as a prioritized list: Breaking first, then Behavioral, then Unsupported. If no incompatibilities are found, state that explicitly so the user has confidence to proceed.

### Step 3 — Query Translation

Ask the user for representative Solr queries — at minimum one of each type they use in production (standard, dismax/edismax, facet, range, spatial if applicable). For each query:

- Call `convert_query` and show the OpenSearch Query DSL equivalent.
- Actively check for query-level incompatibilities and behavioral differences. For each one found, record it in `facts.incompatibilities` with `category: "query"` before moving on.
- Flag queries that cannot be automatically translated and explain what manual work is needed.

Known query incompatibilities to check for:

| Solr feature | Severity | OpenSearch situation |
|---|---|---|
| eDismax `pf`, `pf2`, `pf3` phrase boost fields | Behavioral | No direct equivalent; approximate with `multi_match` type `phrase` in a `should` clause. |
| eDismax `bq` / `bf` additive boost | Behavioral | Use `function_score` or `script_score`; additive vs. multiplicative semantics differ. |
| `{!join}` cross-collection join | Breaking | Not supported; restructure as nested documents or application-side join. |
| `{!collapse}` field collapsing | Behavioral | Use `collapse` via the [Search API collapse parameter](https://opensearch.org/docs/latest/search-plugins/searching-data/collapse/) — available but syntax differs. |
| Solr Streaming Expressions | Unsupported | No equivalent; move aggregation logic to the application layer or use OpenSearch aggregations. |
| `{!graph}` graph traversal | Unsupported | No equivalent in OpenSearch. |
| Spatial `{!geofilt}` / `{!bbox}` | Behavioral | Use `geo_distance` / `geo_bounding_box` queries; parameter names differ. |
| `MoreLikeThis` handler | Behavioral | Use `more_like_this` query; `mindf`, `mintf` parameter names differ slightly. |
| Facet pivots | Behavioral | Use nested `terms` aggregations; result shape differs. |
| `cursorMark` deep pagination | Behavioral | Use `search_after` in OpenSearch; semantics are similar but not identical. |
| Solr relevance TF-IDF (classic) | Behavioral | OpenSearch defaults to BM25; scores will differ. Configurable via `similarity` setting. |

### Step 4 — Solr Customizations

Ask the user whether they rely on any Solr-specific customizations. Use this prompt:

*"Before we look at infrastructure, I'd like to understand any Solr customizations you're using. Do any of the following apply to your deployment? Please describe what you have for each that's relevant:"*

- **Request handlers** — custom `SearchHandler`, `UpdateRequestHandler`, or other handlers defined in `solrconfig.xml`.
- **Plugins** — custom `QParserPlugin`, `SearchComponent`, `TokenFilterFactory`, `UpdateRequestProcessorChain`, or other plugin types.
- **Authentication & authorization** — Basic Auth, Kerberos, PKI, Rule-Based Authorization Plugin, or a custom security plugin.
- **Operational constraints** — specific SLA requirements, air-gapped environments, compliance requirements (e.g. FIPS, FedRAMP), multi-tenancy needs, or read/write traffic isolation.

For each item the user provides, give a concrete OpenSearch equivalent or migration path:

| Solr customization | OpenSearch equivalent / approach |
|---|---|
| Custom `SearchHandler` | Use the [Search API](https://opensearch.org/docs/latest/api-reference/search/) with a custom request body; complex handler logic moves to the application layer or an ingest pipeline. |
| `UpdateRequestProcessorChain` | Replace with an [Ingest Pipeline](https://opensearch.org/docs/latest/ingest-pipelines/) using built-in or custom processors. |
| Custom `QParserPlugin` | Implement equivalent logic in Query DSL (e.g. `function_score`, `script_score`, `percolate`) or a search pipeline. |
| Custom `TokenFilterFactory` / `CharFilterFactory` | Re-express as a custom [analyzer definition](https://opensearch.org/docs/latest/analyzers/) in the index settings using the equivalent built-in filter, or implement a custom plugin via the OpenSearch plugin SDK. |
| Basic Auth | Use the [OpenSearch Security plugin](https://opensearch.org/docs/latest/security/) (bundled) with internal user database or LDAP/Active Directory backend. |
| Kerberos | OpenSearch Security supports Kerberos via the `kerberos` authentication domain. |
| PKI / mutual TLS | Configure node-to-node and client TLS in `opensearch.yml`; the Security plugin handles certificate-based auth. |
| Rule-Based Authorization Plugin | Map to OpenSearch Security [roles and role mappings](https://opensearch.org/docs/latest/security/access-control/). |
| Air-gapped / offline deployment | OpenSearch supports fully offline installation; use the tarball or RPM/DEB packages and mirror the plugin registry internally. |
| FIPS 140-2 compliance | OpenSearch provides a [FIPS-compliant distribution](https://opensearch.org/docs/latest/install-and-configure/install-opensearch/fips/). |
| Multi-tenancy | Use OpenSearch Security [tenants](https://opensearch.org/docs/latest/security/multi-tenancy/) for Dashboards isolation, and index-level permissions for data isolation. |
| Read/write traffic isolation | Route via separate [coordinating-only nodes](https://opensearch.org/docs/latest/tuning-your-cluster/cluster-formation/cluster-manager/) or use a load balancer with separate pools. |

If the user mentions a customization not in the table above, reason about the closest OpenSearch equivalent and flag it as a manual migration item.

Store all identified customizations and their OpenSearch mappings in the session under `facts.customizations` so they are included in the migration report.

### Step 5 — Cluster & Infrastructure Assessment

Ask the user about their current deployment topology:

- Standalone Solr or SolrCloud? Number of nodes, shards, and replicas?
- Approximate document count and index size?
- Peak query throughput and indexing rate?

Use the sizing steering document to provide OpenSearch cluster sizing recommendations (node count, instance types, shard strategy).

### Step 6 — Client & Front-end Integration

Ask the user what client-side code talks to Solr today:

- *"What client libraries are you using — SolrJ, pysolr, a custom HTTP client, or something else?"*
- *"Do you have a front-end search UI (e.g. Solr-specific widgets, Velocity templates, or a custom React/Vue app)?"*

Identify which client calls need to change (endpoint URLs, request/response shapes, authentication) and provide concrete before/after examples where possible.

### Step 7 — Migration Report

Call `generate_report` to produce the final report. The report must cover:

- **Incompatibilities** (prominent, dedicated section at the top of the report) — every item collected in `facts.incompatibilities` across all steps, grouped by severity: Breaking → Behavioral → Unsupported. Each entry must include the category, a description, and the recommended resolution. If there are Breaking or Unsupported items, call them out explicitly as blockers that must be resolved before cutover.
- Major milestones and suggested sequencing.
- Blockers surfaced in Steps 2–6.
- Implementation points with enough detail for an engineer to act on.
- Cost estimates for infrastructure, effort, and any required tooling changes.

Present the report to the user and offer to drill into any section.

## Instructions

- Always maintain the session context using the `session_id`.
- Follow the steps in order. If the user jumps ahead, acknowledge their input, store it in the session, and guide them back to complete any skipped steps.
- If a user asks for migration advice but hasn't provided technical details, proactively request the Solr schema or a sample JSON document (Step 1).
- Use the steering documents (Query Translation, Index Design, Sizing, Incompatibilities) to inform all reasoning.
- **Incompatibility tracking is mandatory.** Every incompatibility found in any step must be recorded in `facts.incompatibilities` before moving on. Never silently skip a known issue.
- When in doubt about whether something is an incompatibility, flag it conservatively — a false positive is far less harmful than a missed breaking change.

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
