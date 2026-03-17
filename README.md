# opensearch-solr-migration-agent-skill

An **Agent Skill** for [OpenSearch](https://opensearch.org/) that helps migrate
from Apache Solr to OpenSearch. Compatible with the
[agentskills.io](https://agentskills.io) format.

## Good example prompts

* "Help me migrate from Solr to OpenSearch."
* "Convert this Solr schema to OpenSearch mapping: <schema>...</schema>"
* "Translate this Solr query to OpenSearch: title:opensearch AND price:[10 TO 100]"
* "Create a migration report for my Solr setup."

## Skills

| Skill | Directory | Description |
|---|---|---|
| Solr to OpenSearch Migration | [`.junie/skills/solr-to-opensearch/`](.junie/skills/solr-to-opensearch/) | Converts Solr schemas and queries to OpenSearch equivalents and provides migration guidance |

Each skill directory contains:
- `SKILL.md` — Machine-readable skill definition (agentskills.io format)
- `README.md` — Human-readable documentation and examples
- `scripts/` — Python source scripts
- `tests/` — Unit tests (if available)

## Example Solr IMDB queries

q=primaryTitle:Inception
q=primaryTitle:Batman AND genres:Action
q=titleType:tvSeries
q=*:*&fq=startYear:[2010 TO 2020]
q=genres:Sci-Fi&sort=startYear desc

## Example Solr Cluster Config

1. SolrCloud with 3 nodes, 2 shards, 2 replicas per shard
2. 40 million documents
3. 50 QPS
4. Indexing rate is 5,000 to 10,000 docs/second
5. Running on AWS m6.ilarge EC2 instances
6. Heap is 8 GB

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