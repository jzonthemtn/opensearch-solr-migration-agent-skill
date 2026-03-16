"""
Solr to OpenSearch Migration Agent Skill.

This package provides functionality for migrating from Apache Solr to OpenSearch,
including schema/mapping conversion, query syntax translation, and migration
guidance. It is designed to be used as an agent skill in the OpenSearch ML
agent framework.
"""

from solr_to_opensearch.schema_converter import SchemaConverter
from solr_to_opensearch.query_converter import QueryConverter
from solr_to_opensearch.skill import SolrToOpenSearchMigrationSkill

__all__ = [
    "SchemaConverter",
    "QueryConverter",
    "SolrToOpenSearchMigrationSkill",
]
