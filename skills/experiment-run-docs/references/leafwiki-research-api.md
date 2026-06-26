# LeafWiki Research API

Use this reference when Codex needs to read or write experiment and operational records in the shared LeafWiki research vault.

## Connection

- Default base URL: `${LEAFWIKI_RESEARCH_BASE_URL:-http://8.134.70.136:8080}`
- Prefer `X-Research-Password: $LEAFWIKI_RESEARCH_API_PASSWORD`.
- Bearer auth is also accepted with `Authorization: Bearer $LEAFWIKI_RESEARCH_API_TOKEN`.
- HTTP Basic auth is accepted; the username can be `research-agent`, and the password is `LEAFWIKI_RESEARCH_API_PASSWORD`.
- Never print secrets. On the user's trusted workstation, load the password without echoing it:

```bash
LEAFWIKI_RESEARCH_API_PASSWORD=$(ssh root@8.134.70.136 "sed -n 's/^LEAFWIKI_RESEARCH_API_PASSWORD=//p' /opt/leafwiki/.env")
```

## Search Before Writing

Search pages before creating a new record:

```bash
curl -fsS "${LEAFWIKI_RESEARCH_BASE_URL:-http://8.134.70.136:8080}/api/research/docs/search?q=<topic>&project=<project>&kind=page&limit=10" \
  -H "X-Research-Password: $LEAFWIKI_RESEARCH_API_PASSWORD"
```

Read full Markdown only after search or recent results identify a relevant `path` or `id`:

```bash
curl -fsS "${LEAFWIKI_RESEARCH_BASE_URL:-http://8.134.70.136:8080}/api/research/docs/read?path=<path>" \
  -H "X-Research-Password: $LEAFWIKI_RESEARCH_API_PASSWORD"
```

Get recent project pages:

```bash
curl -fsS "${LEAFWIKI_RESEARCH_BASE_URL:-http://8.134.70.136:8080}/api/research/docs/recent?project=<project>&kind=page&limit=10" \
  -H "X-Research-Password: $LEAFWIKI_RESEARCH_API_PASSWORD"
```

Browse the project document hierarchy:

```bash
curl -fsS "${LEAFWIKI_RESEARCH_BASE_URL:-http://8.134.70.136:8080}/api/research/docs/tree?project=<project>&kind=page" \
  -H "X-Research-Password: $LEAFWIKI_RESEARCH_API_PASSWORD"
```

`docs/tree` returns `project`, `kind`, `count`, and a recursive `tree`. `count` is the number of nodes that match the requested filters; ancestor sections are still included in `tree` so paths remain navigable. Each node includes `id`, `path`, `title`, `slug`, `kind`, `position`, optional research metadata (`project`, `researchId`, `researchKind`, `status`, `tags`), timestamps, and `children`.

## Create Or Reuse An Experiment

Use a human-readable `slugHint`; the server canonicalizes and de-duplicates the final experiment id. Put stable run identity in `fingerprint` so retries can safely reuse the same record.

```bash
curl -fsS -X POST "${LEAFWIKI_RESEARCH_BASE_URL:-http://8.134.70.136:8080}/api/research/experiments" \
  -H "Content-Type: application/json" \
  -H "X-Research-Password: $LEAFWIKI_RESEARCH_API_PASSWORD" \
  -d '{
    "project": "DeltaKV",
    "title": "Qwen3 SCBench SCDQ ratio 0.2",
    "slugHint": "qwen3-scbench-scdq-r02",
    "status": "running",
    "goal": "Run SCBench SCDQ at ratio 0.2.",
    "command": "bash scripts/tmp/run.sh",
    "workingDir": "/root/autodl-tmp/DeltaKV",
    "repo": "DeltaKV",
    "gitCommit": "<commit>",
    "host": "<host>",
    "model": "Qwen3-4B-Instruct-2507",
    "method": "DeltaKV",
    "benchmark": "SCBench",
    "tags": ["scbench", "scdq"],
    "fingerprint": {
      "run_root": "/data2/outputs/run-a",
      "config": "configs/scbench.yaml"
    }
  }'
```

Response fields include `id`, `pageId`, `path`, `title`, `project`, `status`, `tags`, `fingerprint`, `content`, `created`, and optionally `commitHash`. A duplicate `fingerprint` returns HTTP 200 with `created` false; a new record returns HTTP 201.

## Update An Experiment

Append progress or diagnostic events:

```bash
curl -fsS -X POST "${LEAFWIKI_RESEARCH_BASE_URL:-http://8.134.70.136:8080}/api/research/experiments/<id>/events" \
  -H "Content-Type: application/json" \
  -H "X-Research-Password: $LEAFWIKI_RESEARCH_API_PASSWORD" \
  -d '{
    "title": "Validation started",
    "type": "run",
    "status": "running",
    "content": "GPU job started and log is updating.",
    "metrics": {"expected_rows": 500},
    "artifacts": [{"label": "stdout", "path": "/data2/outputs/run-a/stdout.log"}]
  }'
```

Update status:

```bash
curl -fsS -X PATCH "${LEAFWIKI_RESEARCH_BASE_URL:-http://8.134.70.136:8080}/api/research/experiments/<id>/status" \
  -H "Content-Type: application/json" \
  -H "X-Research-Password: $LEAFWIKI_RESEARCH_API_PASSWORD" \
  -d '{"status":"completed","note":"All expected rows are present."}'
```

Record final or partial results:

```bash
curl -fsS -X POST "${LEAFWIKI_RESEARCH_BASE_URL:-http://8.134.70.136:8080}/api/research/experiments/<id>/results" \
  -H "Content-Type: application/json" \
  -H "X-Research-Password: $LEAFWIKI_RESEARCH_API_PASSWORD" \
  -d '{
    "status": "completed",
    "content": "Final score is stable against the baseline.",
    "metrics": {"accuracy": 0.91},
    "artifacts": [{"label": "summary", "path": "/data2/outputs/run-a/summary.json"}]
  }'
```

## Read Experiment Context

Read the current experiment plus related and recent project docs:

```bash
curl -fsS "${LEAFWIKI_RESEARCH_BASE_URL:-http://8.134.70.136:8080}/api/research/experiments/<id>/context?q=<topic>&limit=10" \
  -H "X-Research-Password: $LEAFWIKI_RESEARCH_API_PASSWORD"
```

This returns `experiment`, `query`, `relatedDocs`, and `recentDocs`. The context endpoint excludes the experiment itself from related/recent docs.

## List And Fetch Experiments

```bash
curl -fsS "${LEAFWIKI_RESEARCH_BASE_URL:-http://8.134.70.136:8080}/api/research/experiments?project=<project>&status=<status>" \
  -H "X-Research-Password: $LEAFWIKI_RESEARCH_API_PASSWORD"

curl -fsS "${LEAFWIKI_RESEARCH_BASE_URL:-http://8.134.70.136:8080}/api/research/experiments/<id>" \
  -H "X-Research-Password: $LEAFWIKI_RESEARCH_API_PASSWORD"
```

## Error Shape

Research API errors use:

```json
{"error":{"code":"invalid_research_input","message":"invalid research input: q is required"}}
```

Common codes: `invalid_research_input`, `experiment_not_found`, `document_not_found`, and `search_unavailable`.
