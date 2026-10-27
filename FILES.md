# Find every shipped file

The root documents explain adoption. Each skill keeps its entrypoint, selected references, synthetic assets and verifier together. Copy the complete skill folder when installing it.

```text
claude-skills-rag-semantic-d3-analytics/
├── README.md
├── CLAUDE.md
├── AGENTS.md
├── FILES.md
├── .gitignore
└── .claude/
    └── skills/
        ├── d3-sql-design/
        │   ├── SKILL.md
        │   ├── requirements.txt
        │   ├── assets/
        │   │   ├── chart-contract.schema.json
        │   │   ├── checked-examples.json
        │   │   ├── events.json
        │   │   ├── field-contract.schema.json
        │   │   ├── field-examples.json
        │   │   ├── prompt-output.json
        │   │   └── system-prompt.md
        │   ├── references/
        │   │   ├── contracts-and-aliases.md
        │   │   ├── extension-and-verification.md
        │   │   ├── generation-prompt.md
        │   │   ├── prepared-data.md
        │   │   ├── rendering-lifecycle.md
        │   │   ├── rules-engine.md
        │   │   ├── sql-and-aggregation.md
        │   │   ├── view-changes.md
        │   │   └── worked-examples.md
        │   └── scripts/
        │       └── verify_examples.py
        ├── rag-design/
        │   ├── SKILL.md
        │   ├── assets/
        │   │   └── contract-examples.json
        │   ├── references/
        │   │   ├── entity-resolution.md
        │   │   ├── governed-ingestion-and-serving.md
        │   │   ├── knowledge-navigation.md
        │   │   ├── lexical-and-hybrid-retrieval.md
        │   │   ├── long-form-ingestion.md
        │   │   ├── pipeline-context-and-compilation.md
        │   │   ├── questions-and-examples.md
        │   │   └── semantic-field-corpus.md
        │   └── scripts/
        │       └── verify_contracts.py
        └── semantic-layer-design/
            ├── SKILL.md
            ├── assets/
            │   ├── reconstruction-workbook.json
            │   └── semantic-contract.schema.json
            ├── references/
            │   ├── 00-consumers-and-evidence.md
            │   ├── 01-sql-intake-and-identity.md
            │   ├── 02-column-profiles-and-enhancement.md
            │   ├── 03-column-semantics-and-facets.md
            │   ├── 04-query-semantics-and-contracts.md
            │   ├── 05-value-samples-and-cooccurrence.md
            │   ├── 06-entity-resolution-and-semantic-retrieval.md
            │   ├── 07-runtime-catalog-and-consumers.md
            │   ├── 08-portable-and-governed-compilation.md
            │   ├── 09-orchestration-and-reconstruction.md
            │   ├── field-and-metric-contracts.md
            │   └── quality-and-enforcement.md
            └── scripts/
                └── verify_contracts.py
```

## Choose the right starting point

| Start with | Then follow |
| --- | --- |
| [README.md](README.md) | The skill/outcome table, architecture diagram and example requests. |
| [CLAUDE.md](CLAUDE.md) | Installation, invocation, combined use, optional checks and maintenance. `AGENTS.md` is an identical portable instruction mirror. |
| [Semantic-layer entrypoint](.claude/skills/semantic-layer-design/SKILL.md) | The selected method for field meaning, metrics, evidence, catalogs or compilation. |
| [RAG entrypoint](.claude/skills/rag-design/SKILL.md) | The selected method for ingestion, retrieval, resolution, citations or publication. |
| [SQL-to-D3 entrypoint](.claude/skills/d3-sql-design/SKILL.md) | The selected method for SQL/result contracts, aliases, view changes or rendering lifecycle. |

The `.gitignore` keeps local working artifacts out of publication. No application runtime is bundled.
