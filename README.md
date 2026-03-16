# opensearch-solr-migration-agent-skill

An **Agent Skill** for [OpenSearch](https://opensearch.org/) that helps migrate
from Apache Solr to OpenSearch. Compatible with the
[agentskills.io](https://agentskills.io) format.

## Skills

| Skill | Directory | Description |
|---|---|---|
| Solr to OpenSearch Migration | [`.junie/skills/solr-to-opensearch/`](.junie/skills/solr-to-opensearch/) | Converts Solr schemas and queries to OpenSearch equivalents and provides migration guidance |

Each skill directory contains:
- `SKILL.md` — Machine-readable skill definition (agentskills.io format)
- `README.md` — Human-readable documentation and examples
- `scripts/` — Python source scripts
- `tests/` — Unit tests (if available)

## Getting Started

```bash
cd .junie/skills/solr-to-opensearch
pip install -e ".[dev]"
python - <<'EOF'
import sys
import os
# Add scripts directory to sys.path
sys.path.append(os.path.join(os.getcwd(), "scripts"))

from skill import SolrToOpenSearchMigrationSkill

skill = SolrToOpenSearchMigrationSkill()
print(skill.convert_query("title:opensearch AND price:[10 TO 100]"))
EOF
```

## License

Apache-2.0