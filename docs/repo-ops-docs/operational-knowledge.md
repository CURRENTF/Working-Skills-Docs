# Operational Knowledge Capture

Use this guide for non-code knowledge that makes a repo runnable: training services, inference servers, UE data generation, dataset downloads, model caches, long-running jobs, and recurring runtime issues.

## Placement

- Project-specific details belong in that project repo under `docs/`.
- Reusable procedures belong in `Working-Skills-Docs/docs/`.
- If a workflow is both project-specific and reusable, keep exact commands in the project repo and keep the generalized pattern here.

## What Good Docs Include

- Working directory and environment activation.
- Exact start command and important config files.
- Required ports, host binding, GPU/device assumptions, and storage paths.
- Verification command or health check.
- Stop/restart procedure.
- Output locations and expected file shape.
- Common failures with checks and fixes.

## Workflow Templates

### Training Server

```markdown
# Training Server

## Prerequisites

## Paths

## Start

## Verify

## Stop

## Checkpoints And Logs

## Resume

## Troubleshooting
```

### UE Data Generation Server

```markdown
# UE Data Generation Server

## Prerequisites

## Scene Or Map

## Start UE

## Start Client

## Verify

## Stop

## Outputs

## Troubleshooting
```

### Dataset Download

```markdown
# Dataset Download

## Source

## Target Path

## Download

## Verify

## Resume Or Retry

## Disk Usage

## Notes
```

## Notes On Confidence

Mark information as tested only after running it. For user-provided or README-derived steps that were not executed, write `From project docs` or `User-provided` so later readers know the confidence level.
