"""
MCP stdio server for the Solr to OpenSearch Migration Advisor skill.

Run directly:
    python mcp_server.py

Or configure in your MCP client (.kiro/settings/mcp.json):
    {
      "mcpServers": {
        "solr-to-opensearch": {
          "command": "python3",
          "args": [".kiro/skills/solr-to-opensearch/scripts/mcp_server.py"]
        }
      }
    }
"""

import sys
import os

# Ensure the scripts directory is on the path when invoked directly.
sys.path.insert(0, os.path.dirname(__file__))

from mcp.server.fastmcp import FastMCP
from skill import SolrToOpenSearchMigrationSkill

mcp = FastMCP("solr-to-opensearch")
_skill = SolrToOpenSearchMigrationSkill()


@mcp.tool()
def handle_message(message: str, session_id: str) -> str:
    """Send a message to the Solr to OpenSearch migration advisor.

    Supports schema conversion (paste your schema.xml), query translation,
    migration checklists, and report generation. Session state is persisted
    across calls using session_id.

    Args:
        message: The user message or request.
        session_id: A unique identifier for the migration session.

    Returns:
        The advisor's response as a string.
    """
    return _skill.handle_message(message, session_id)


@mcp.tool()
def generate_report(session_id: str) -> str:
    """Generate a comprehensive migration report for the given session.

    Produces a structured report covering major milestones, potential blockers,
    implementation points, and cost estimates based on the session's history.

    Args:
        session_id: The session identifier used during the migration conversation.

    Returns:
        A Markdown-formatted migration report.
    """
    return _skill.generate_report(session_id)


@mcp.tool()
def convert_schema_xml(schema_xml: str) -> str:
    """Convert a Solr schema.xml document to an OpenSearch index mapping.

    Args:
        schema_xml: The full text content of a Solr schema.xml file.

    Returns:
        A JSON string representing the OpenSearch index mapping.
    """
    return _skill.convert_schema_xml(schema_xml)


@mcp.tool()
def convert_schema_json(schema_api_json: str) -> str:
    """Convert a Solr Schema API JSON response to an OpenSearch index mapping.

    The Solr Schema API is available at GET /solr/<collection>/schema.

    Args:
        schema_api_json: JSON string returned by the Solr Schema API.

    Returns:
        A JSON string representing the OpenSearch index mapping.
    """
    return _skill.convert_schema_json(schema_api_json)


@mcp.tool()
def convert_query(solr_query: str) -> str:
    """Translate a Solr query string to an OpenSearch Query DSL JSON string.

    Supports field:value, phrase, wildcard, range, boolean (AND/OR/NOT),
    and match_all (*:*) patterns.

    Args:
        solr_query: A Solr query string (the value of the q parameter).

    Returns:
        A JSON string representing the OpenSearch Query DSL.
    """
    return _skill.convert_query(solr_query)


@mcp.tool()
def get_migration_checklist() -> str:
    """Return a human-readable checklist of all migration steps.

    Covers preparation, schema migration, index settings, query migration,
    data migration, client migration, testing, and cutover.

    Returns:
        A plain-text migration checklist.
    """
    return _skill.get_migration_checklist()


@mcp.tool()
def get_field_type_mapping_reference() -> str:
    """Return a Markdown reference table of Solr to OpenSearch field type mappings.

    Returns:
        A Markdown-formatted table mapping Solr field type class names to
        their OpenSearch equivalents.
    """
    return _skill.get_field_type_mapping_reference()


if __name__ == "__main__":
    mcp.run(transport="stdio")
