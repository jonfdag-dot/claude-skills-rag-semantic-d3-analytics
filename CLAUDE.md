# Install and use the analytics skills

Add the three skill folders to Claude Code, then use them in the application you are building. This repository packages design instructions, supporting references and synthetic contract examples; the application owns its runtime and verification.

## Copy complete skill folders

Clone or download [this repository](https://github.com/jonfdag-dot/claude-skills-rag-semantic-d3-analytics). Copy each complete folder from `.claude/skills/`, including its `SKILL.md`, references, assets, scripts and any requirements file.

Choose the installation scope that fits your work:

| Scope | Copy the three folders into | Available to |
| --- | --- | --- |
| Personal | `~/.claude/skills/` | Local Claude Code sessions across your projects. |
| Project | `<your-project>/.claude/skills/` | Claude Code sessions in that repository. Commit the folders if you want to share them with collaborators. |

The folders are `semantic-layer-design`, `rag-design` and `d3-sql-design`. Compare any same-named skill before copying. Preserve your existing version until you have reviewed a merge or chosen a backup and replacement. Merge any working conventions you want into your application's existing instructions; preserve that project's rules.

These are native skill directories. [Claude Code documents the supported paths and direct `/skill-name` invocation](https://code.claude.com/docs/en/skills). Open a fresh Claude Code session in your application repository, type `/` to inspect the available skills, and confirm the names resolve to the installation you intend to use.

## Invoke the skill for your task

| Command | Start here when you need to |
| --- | --- |
| `/semantic-layer-design` | Define field meaning, metric contracts, entity evidence, reviewed edits or a consumer-ready catalog. |
| `/rag-design` | Design ingestion, evidence selection, lexical/hybrid retrieval, entity resolution or grounded context. |
| `/d3-sql-design` | Carry metric meaning from a question through SQL, result rows, D3 preparation and view changes. |

Include the intended consumer, authorized source, available schema or documents, required output, constraints and acceptance checks. Supply relevant existing artifacts when changing a system. Ask for the references needed by the task; each entrypoint provides a selection table. The [README prompts](README.md#try-one-bounded-task) show bounded starting requests.

## Combine the skills around one consumer

For an analytics assistant, start with the contract it must satisfy, then use the relevant skills in this order:

1. Use `semantic-layer-design` to define the admitted source, field identities, metric population and grain, reviewed meaning, and the catalog your consumer receives.
2. Use `rag-design` to construct and select evidence for that consumer. Preserve source revisions, authenticated scope, readiness and citations, and define how ambiguity or incomplete coverage is reported.
3. Use `d3-sql-design` to carry those definitions into query contracts, exact aliases, result validation, prepared chart data, and update/disposal behavior.

Carry the produced contracts into the next task and reconcile names, enums and record shapes explicitly. These guides describe related methods; they do not install a shared database schema or an automatic pipeline. If your application already has one of these stages, inspect that implementation and adapt the affected boundary.

Implement and test the selected design in your application. Keep permission checks, SQL safety, complete-result checks and chart lifecycle enforcement in executable code. A prompt, schema or successful example check does not enforce those properties in a deployed system.

## Run the optional example checks

Reading and using the guides needs Claude Code. Running the synthetic examples also needs Python. Run the following commands from this repository's root, or adjust them to the installed skill paths.

Use Python 3.12, the tested version for these examples. The RAG and semantic-layer verifiers use only the standard library. The semantic-layer verifier uses its SQLite module and an in-memory synthetic database.

```sh
python3 -B .claude/skills/rag-design/scripts/verify_contracts.py
python3 -B .claude/skills/semantic-layer-design/scripts/verify_contracts.py
```

The D3 examples are tested with Python 3.12 and use the pinned `jsonschema` dependency in [requirements.txt](.claude/skills/d3-sql-design/requirements.txt). Use an isolated environment:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r .claude/skills/d3-sql-design/requirements.txt
.venv/bin/python -B .claude/skills/d3-sql-design/scripts/verify_examples.py
```

The D3 verifier also needs IANA timezone data for `America/New_York`. If your platform lacks system timezone data, install `tzdata` into that environment. See the [D3 check instructions](.claude/skills/d3-sql-design/references/extension-and-verification.md#run-package-checks) for the tested setup and limits.

These scripts exercise supplied synthetic fixtures. They make no model calls and require no credentials, private checkout or database server. A pass establishes the checked example contracts, not model compliance, retrieval quality, arbitrary SQL safety, PostgreSQL execution, browser cleanup or performance. Report actual commands, results and unrun checks when adopting a design.

## Maintain only the requested surface

Keep each skill and its resources together, preserve existing user changes, and limit edits to the requested outcome. Check changed relative links and JSON, then run the affected deterministic example verifier when its contracts or fixtures change. Ordinary documentation maintenance does not require model evaluations. Keep `AGENTS.md` byte-identical to this guide; it mirrors the portable instructions, while the packaged skills and commands target Claude Code.

Shared research and plan libraries are optional. If you use them, configure their locations in your application's instructions, search retained findings before new research, and follow each library's own indexing and validation rules. Store durable plans outside this repository in an adopter-configured location. No personal library path or companion kit is required to use these skills.

Publish only with explicit approval. If the adopter has a configured `ship-it` workflow, use it; otherwise follow the repository's approved publication process.

[Return to the overview](README.md) · [Browse every file](FILES.md)
