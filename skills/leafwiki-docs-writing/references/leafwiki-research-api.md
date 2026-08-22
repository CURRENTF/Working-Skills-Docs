# LeafWiki Research API

Read this reference before calling or modifying LeafWiki research-vault API
requests.

## Connection

- Default base URL: `${LEAFWIKI_RESEARCH_BASE_URL:-http://8.134.70.136:8080}`
- Prefer `X-Research-Password: $LEAFWIKI_RESEARCH_API_PASSWORD`.
- Bearer auth is accepted with
  `Authorization: Bearer $LEAFWIKI_RESEARCH_API_TOKEN`.
- Never print secrets. On the user's trusted workstation, if process env vars
  are missing, first load the user-global dotenv without echoing values:

```bash
if [ -z "${LEAFWIKI_RESEARCH_API_PASSWORD:-}" ] && [ -f /home/haojitai/.env ]; then
  set -a
  . /home/haojitai/.env
  set +a
fi
```

- If both process env vars and `/home/haojitai/.env` are missing, and SSH
  works, load the password from the server without echoing it:

```bash
LEAFWIKI_RESEARCH_API_PASSWORD=$(ssh root@8.134.70.136 "sed -n 's/^LEAFWIKI_RESEARCH_API_PASSWORD=//p' /opt/leafwiki/.env")
```

## Search And Read

Search pages before creating records:

```bash
curl -fsS "${LEAFWIKI_RESEARCH_BASE_URL:-http://8.134.70.136:8080}/api/research/docs/search?q=<topic>&project=<project>&kind=page&limit=10" \
  -H "X-Research-Password: $LEAFWIKI_RESEARCH_API_PASSWORD"
```

Read full Markdown only after search identifies a relevant `path`:

```bash
curl -fsS "${LEAFWIKI_RESEARCH_BASE_URL:-http://8.134.70.136:8080}/api/research/docs/read?path=<path>" \
  -H "X-Research-Password: $LEAFWIKI_RESEARCH_API_PASSWORD"
```

Get recent project pages:

```bash
curl -fsS "${LEAFWIKI_RESEARCH_BASE_URL:-http://8.134.70.136:8080}/api/research/docs/recent?project=<project>&kind=page&limit=10" \
  -H "X-Research-Password: $LEAFWIKI_RESEARCH_API_PASSWORD"
```

## Create Or Reuse A Record

Use `POST /api/research/experiments` for auditable experiment, evaluation, and
operations records. The server canonicalizes `slugHint` and de-duplicates by
`fingerprint`.

```bash
curl -fsS -X POST "${LEAFWIKI_RESEARCH_BASE_URL:-http://8.134.70.136:8080}/api/research/experiments" \
  -H "Content-Type: application/json" \
  -H "X-Research-Password: $LEAFWIKI_RESEARCH_API_PASSWORD" \
  -d '{
    "project": "Sparse-vLLM",
    "title": "Qwen3 Claw Eval T062 Local Judge Smoke",
    "slugHint": "qwen3-claw-eval-t062-localjudge-smoke",
    "status": "completed",
    "goal": "Validate the Sparse-vLLM OpenAI shim on one Claw-Eval task.",
    "command": "bash benchmark/claw_eval/run_sparsevllm_claw_eval.sh",
    "workingDir": "/home/haojitai/projects/Sparse-vLLM",
    "repo": "Sparse-vLLM",
    "gitCommit": "<commit>",
    "host": "<host>",
    "model": "Qwen3-4B-Instruct-2507",
    "method": "vanilla",
    "benchmark": "Claw-Eval",
    "tags": ["claw-eval", "openai-shim"],
    "fingerprint": {
      "run_root": "/data2/haojitai/outputs/Sparse-vLLM/claw-eval/<run_id>",
      "task": "T062_finance_pltr_cagr"
    }
  }'
```

Response fields include `id`, `pageId`, `path`, `title`, `project`, `status`,
`tags`, `fingerprint`, `content`, `created`, and optionally `commitHash`.
Duplicate fingerprints return HTTP 200 with `created: false`; new records
return HTTP 201.

## Update A Record

Append progress or diagnostics:

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

## Context And Listing

```bash
curl -fsS "${LEAFWIKI_RESEARCH_BASE_URL:-http://8.134.70.136:8080}/api/research/experiments/<id>/context?q=<topic>&limit=10" \
  -H "X-Research-Password: $LEAFWIKI_RESEARCH_API_PASSWORD"

curl -fsS "${LEAFWIKI_RESEARCH_BASE_URL:-http://8.134.70.136:8080}/api/research/experiments?project=<project>&status=<status>" \
  -H "X-Research-Password: $LEAFWIKI_RESEARCH_API_PASSWORD"

curl -fsS "${LEAFWIKI_RESEARCH_BASE_URL:-http://8.134.70.136:8080}/api/research/experiments/<id>" \
  -H "X-Research-Password: $LEAFWIKI_RESEARCH_API_PASSWORD"
```

## Errors

Research API errors use:

```json
{"error":{"code":"invalid_research_input","message":"invalid research input: q is required"}}
```

Common codes include `invalid_research_input`, `experiment_not_found`,
`document_not_found`, and `search_unavailable`. Fail visibly; do not silently
fall back to repo-local private indexes.
