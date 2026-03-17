"""
Main agent skill class for migrating from Apache Solr to OpenSearch.

The :class:`SolrToOpenSearchMigrationSkill` class acts as a high-level facade
that can be used as an agent tool in the OpenSearch ML agent framework.  Each
public method corresponds to a discrete migration capability that an agent can
invoke.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional, List

from schema_converter import SchemaConverter
from query_converter import QueryConverter
from storage import StorageInterface, FileStorage
from report import MigrationReport


class SolrToOpenSearchMigrationSkill:
    """Agent skill for migrating from Apache Solr to OpenSearch.

    This skill exposes the following capabilities:

    * :meth:`convert_schema_xml` — Translate a Solr ``schema.xml`` document
      into an OpenSearch index mapping JSON string.
    * :meth:`convert_schema_json` — Translate a Solr Schema API JSON document
      into an OpenSearch index mapping JSON string.
    * :meth:`convert_query` — Translate a Solr query string into an
      OpenSearch Query DSL JSON string.
    * :meth:`get_migration_checklist` — Return a human-readable checklist of
      migration steps from Solr to OpenSearch.
    * :meth:`generate_report` — Generate a comprehensive migration report.
    * :meth:`handle_message` — Transport-agnostic message handler for the advisor.

    Usage::

        skill = SolrToOpenSearchMigrationSkill()
        response = skill.handle_message("Convert this schema...", session_id="user-123")
    """

    def __init__(self, storage: Optional[StorageInterface] = None) -> None:
        self._schema_converter = SchemaConverter()
        self._query_converter = QueryConverter()
        self._storage = storage or FileStorage()
        self._steering_docs = self._load_steering_docs()

    def _load_steering_docs(self) -> Dict[str, str]:
        """Load steering documents from the data directory."""
        docs = {}
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "steering")
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                if filename.endswith(".md"):
                    with open(os.path.join(data_dir, filename), "r") as f:
                        docs[filename[:-3]] = f.read()
        return docs

    def handle_message(self, message: str, session_id: str) -> str:
        """Transport-agnostic core interface.
        
        Args:
            message: The user's message.
            session_id: The session handle for persistent memory.
            
        Returns:
            A string response from the agent.
        """
        # Load or initialize session state
        session_data = self._storage.load(session_id) or {
            "history": [],
            "facts": {},
            "progress": 0
        }
        
        # Simple rule-based routing for this implementation
        message_lc = message.lower()
        response = ""

        # Schema conversion: detect XML schema block in the message
        schema_start = message.find("<schema")
        schema_end = message.find("</schema>")
        has_schema_xml = schema_start != -1 and schema_end != -1

        if "report" in message_lc:
            response = self.generate_report(session_id)
        elif has_schema_xml or (
            ("schema" in message_lc or "migrate" in message_lc or "convert" in message_lc)
            and "<schema" in message
        ):
            if has_schema_xml:
                schema_xml = message[schema_start:schema_end + 9]
                mapping = self.convert_schema_xml(schema_xml)
                response = f"I've converted your Solr schema to an OpenSearch mapping:\n\n```json\n{mapping}\n```"
                session_data["facts"]["schema_migrated"] = True
            else:
                response = "I detected you want to convert a schema, but I couldn't find the XML content. Please paste your full `schema.xml` content."
        elif "query" in message_lc or "translate" in message_lc:
            # Extract the query string: look for content after a colon or the keyword
            q = ""
            for keyword in ("query:", "query", "translate:"):
                idx = message_lc.find(keyword)
                if idx != -1:
                    q = message[idx + len(keyword):].strip().lstrip(": ").strip()
                    break
            if q:
                try:
                    dsl = self.convert_query(q)
                    response = f"The OpenSearch equivalent of your query is:\n\n```json\n{dsl}\n```"
                except ValueError:
                    response = "I couldn't parse that query. Please provide a valid Solr query string (e.g. `title:opensearch AND year:[2020 TO *]`)."
            else:
                response = "What query would you like me to translate?"
        elif "checklist" in message_lc:
            response = self.get_migration_checklist()
        elif "field type" in message_lc or "type mapping" in message_lc:
            response = self.get_field_type_mapping_reference()
        else:
            response = "I'm your Solr to OpenSearch migration advisor. How can I help you today? I can convert schemas, translate queries, or generate a migration report."

        # Update session memory
        session_data["history"].append({"user": message, "assistant": response})
        self._storage.save(session_id, session_data)
        
        return response

    def generate_report(self, session_id: str) -> str:
        """Generate a concrete migration report for the session."""
        session_data = self._storage.load(session_id) or {}
        facts = session_data.get("facts", {})
        
        milestones = [
            "Infrastructure setup and sizing",
            "Schema and analysis chain migration",
            "Data re-indexing and validation",
            "Application query and client migration",
            "Parallel testing and cutover"
        ]
        
        blockers = []
        if not facts.get("schema_migrated"):
            blockers.append("Schema not yet analyzed for incompatibilities.")
        
        ip = [
            "Map Solr field types to OpenSearch equivalents (see steering documents).",
            "Replace Solr copyField with OpenSearch copy_to.",
            "Update client libraries from SolrJ/SolrPy to OpenSearch clients."
        ]
        
        costs = {
            "Infrastructure": "Estimated 10% increase over Solr due to shard management overhead.",
            "Effort": "Moderate (2-4 weeks for typical mid-sized workload)."
        }
        
        report = MigrationReport(milestones, blockers, ip, costs)
        return report.generate()


    # ------------------------------------------------------------------
    # Schema conversion
    # ------------------------------------------------------------------

    def convert_schema_xml(
        self, schema_xml: str, *, indent: int = 2
    ) -> str:
        """Convert a Solr ``schema.xml`` to an OpenSearch index mapping.

        Args:
            schema_xml: The full text content of a Solr ``schema.xml`` file.
            indent: JSON indentation level for the returned string.

        Returns:
            A JSON string representing the OpenSearch index mapping.

        Raises:
            ValueError: If the XML cannot be parsed or is not a valid Solr
                schema.
        """
        mapping = self._schema_converter.convert_xml(schema_xml)
        return json.dumps(mapping, indent=indent)

    def convert_schema_json(
        self, schema_api_json: str, *, indent: int = 2
    ) -> str:
        """Convert a Solr Schema API JSON document to an OpenSearch mapping.

        The Solr Schema API endpoint is typically available at::

            GET /solr/<collection>/schema

        Args:
            schema_api_json: JSON string returned by the Solr Schema API.
            indent: JSON indentation level for the returned string.

        Returns:
            A JSON string representing the OpenSearch index mapping.

        Raises:
            ValueError: If the JSON cannot be parsed or is missing required
                keys.
        """
        mapping = self._schema_converter.convert_json(schema_api_json)
        return json.dumps(mapping, indent=indent)

    # ------------------------------------------------------------------
    # Query conversion
    # ------------------------------------------------------------------

    def convert_query(self, solr_query: str, *, indent: int = 2) -> str:
        """Convert a Solr query string to an OpenSearch Query DSL JSON string.

        Args:
            solr_query: A Solr query string (the value of the ``q`` parameter).
            indent: JSON indentation level for the returned string.

        Returns:
            A JSON string representing the OpenSearch Query DSL.

        Raises:
            ValueError: If ``solr_query`` is empty.
        """
        dsl = self._query_converter.convert(solr_query)
        return json.dumps(dsl, indent=indent)

    # ------------------------------------------------------------------
    # Migration guidance
    # ------------------------------------------------------------------

    def get_migration_checklist(self) -> str:
        """Return a human-readable checklist of migration steps.

        Returns:
            A plain-text checklist string covering the key areas to address
            when migrating from Solr to OpenSearch.
        """
        return _MIGRATION_CHECKLIST

    def get_field_type_mapping_reference(self) -> str:
        """Return a reference table of Solr → OpenSearch field type mappings.

        Returns:
            A Markdown-formatted reference table as a string.
        """
        from schema_converter import SOLR_TYPE_TO_OPENSEARCH

        lines: list[str] = [
            "| Solr Field Type | OpenSearch Type |",
            "|---|---|",
        ]
        seen: dict[str, str] = {}
        for solr_type, os_type in SOLR_TYPE_TO_OPENSEARCH.items():
            # Show only the short name (without "solr." prefix) to keep the
            # table concise.
            short = solr_type.replace("solr.", "")
            if short not in seen:
                seen[short] = os_type
                lines.append(f"| {short} | {os_type} |")

        return "\n".join(lines)

_MIGRATION_CHECKLIST: str = """\
Apache Solr → OpenSearch Migration Checklist
=============================================

1. PREPARATION
   [ ] Back up all Solr collections and configuration files.
   [ ] Document all Solr field types, fields, and dynamic fields.
   [ ] Record all custom tokenizers, filters, and analyzers.
   [ ] List all Solr request handlers, search components, and plugins.
   [ ] Identify any SolrCloud-specific configuration (ZooKeeper, shards,
       replicas).

2. SCHEMA / MAPPING MIGRATION
   [ ] Convert Solr schema.xml to an OpenSearch index mapping using the
       convert_schema_xml() skill method.
   [ ] Review the generated mapping for accuracy and completeness.
   [ ] Map custom Solr field types to appropriate OpenSearch types.
   [ ] Translate custom analyzers (char filters, tokenizers, token filters)
       to OpenSearch analysis settings.
   [ ] Handle multi-valued fields (OpenSearch arrays are native).
   [ ] Replace Solr copyField directives with OpenSearch copy_to.

3. INDEX SETTINGS
   [ ] Define OpenSearch index settings (number_of_shards,
       number_of_replicas, refresh_interval, etc.).
   [ ] Translate Solr synonyms.txt and stopwords.txt to OpenSearch analysis
       synonym / stop token filter configuration.
   [ ] Configure dynamic mappings or disable them to match Solr's
       schemaFactory setting.

4. QUERY MIGRATION
   [ ] Identify all query types in use (standard, edismax, dismax, spatial,
       facet, etc.).
   [ ] Convert standard Solr queries to OpenSearch Query DSL using the
       convert_query() skill method.
   [ ] Translate eDismax parameters (qf, pf, mm, boost, etc.) to
       OpenSearch multi_match / function_score queries.
   [ ] Migrate facet queries to OpenSearch aggregations.
   [ ] Replace Solr highlighting parameters with OpenSearch highlight API.
   [ ] Convert Solr spatial queries to OpenSearch geo_distance / geo_shape
       queries.
   [ ] Migrate Solr MoreLikeThis queries to OpenSearch more_like_this.

5. DATA MIGRATION
   [ ] Choose a migration strategy:
       a) Re-index from source data (recommended for clean migration).
       b) Export from Solr via Data Import Handler or curl and import into
          OpenSearch using the Bulk API.
   [ ] Validate document counts and spot-check field values after migration.

6. APPLICATION / CLIENT MIGRATION
   [ ] Replace the Solr Java/Python/Ruby client with the appropriate
       OpenSearch client.
   [ ] Update HTTP endpoints (Solr uses /solr/<collection>/select;
       OpenSearch uses /<index>/_search).
   [ ] Migrate Solr Admin UI usage to OpenSearch Dashboards.
   [ ] Replace SolrCloud management API calls with OpenSearch Cluster API
       calls.

7. TESTING
   [ ] Run query equivalence tests: same inputs should return equivalent
       results from both Solr and OpenSearch.
   [ ] Validate relevance scores and ranking.
   [ ] Load-test the OpenSearch cluster under production-level traffic.
   [ ] Test failover and replica behaviour.

8. CUTOVER
   [ ] Run both systems in parallel and compare results.
   [ ] Switch application traffic to OpenSearch.
   [ ] Monitor OpenSearch cluster health and query latency.
   [ ] Decommission Solr after a suitable stabilization period.

USEFUL OPENSEARCH DOCUMENTATION
--------------------------------
* Index API:        https://opensearch.org/docs/latest/api-reference/index-apis/
* Mapping:          https://opensearch.org/docs/latest/field-types/
* Query DSL:        https://opensearch.org/docs/latest/query-dsl/
* Aggregations:     https://opensearch.org/docs/latest/aggregations/
* Analysis:         https://opensearch.org/docs/latest/analyzers/
* Migration guide:  https://opensearch.org/docs/latest/migration-guide/
"""
