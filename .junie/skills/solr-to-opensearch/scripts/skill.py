"""
Main agent skill class for migrating from Apache Solr to OpenSearch.

The :class:`SolrToOpenSearchMigrationSkill` class acts as a high-level facade
that can be used as an agent tool in the OpenSearch ML agent framework.  Each
public method corresponds to a discrete migration capability that an agent can
invoke.
"""

from __future__ import annotations

import json
from typing import Any

from schema_converter import SchemaConverter
from .query_converter import QueryConverter


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

    Usage::

        skill = SolrToOpenSearchMigrationSkill()

        mapping_json = skill.convert_schema_xml(open("schema.xml").read())
        query_dsl_json = skill.convert_query("title:opensearch AND category:docs")

        print(mapping_json)
        print(query_dsl_json)
    """

    def __init__(self) -> None:
        self._schema_converter = SchemaConverter()
        self._query_converter = QueryConverter()

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
        from solr_to_opensearch.schema_converter import SOLR_TYPE_TO_OPENSEARCH

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


# ---------------------------------------------------------------------------
# Static content
# ---------------------------------------------------------------------------

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
