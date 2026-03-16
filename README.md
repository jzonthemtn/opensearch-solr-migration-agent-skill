# opensearch-agent-skills

A collection of **Agent Skills** for [OpenSearch](https://opensearch.org/). Each skill is a self-contained Python package that can be used as a tool within the [OpenSearch ML agent framework](https://opensearch.org/docs/latest/ml-commons-plugin/agents-tools/index/) or invoked directly from application code.

## Skills

| Skill | Directory | Description |
|---|---|---|
| Solr to OpenSearch Migration | [`solr-to-opensearch/`](solr-to-opensearch/) | Converts Solr schemas and queries to OpenSearch equivalents and provides migration guidance |

## Getting Started

Each skill is an independent Python package. Navigate to the skill directory and follow its README for installation and usage instructions.

```bash
# Example: install and use the Solr-to-OpenSearch migration skill
cd solr-to-opensearch
pip install -e ".[dev]"
python - <<'EOF'
from solr_to_opensearch import SolrToOpenSearchMigrationSkill

skill = SolrToOpenSearchMigrationSkill()
print(skill.convert_query("title:opensearch AND price:[10 TO 100]"))
EOF
```

## License

Apache-2.0