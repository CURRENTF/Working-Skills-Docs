---
name: goal-draft-review
description: Turn a user's rough requirement into a precise, reviewable Codex goal draft before setting an actual /goal. Use when the user wants a goal proposal, goal wording, goal pipeline, low-token goal strategy, Codex goal implementation-aware advice, or asks to convert a task into a goal for review. Do not create or update the active goal until the user explicitly approves the draft.
---

# Goal Draft Review

Use this skill to convert a request into a goal proposal the user can review before it becomes an active `/goal`.

## Core Rule

Draft first. Do not call `create_goal` or set `/goal` unless the user explicitly approves the final goal text and budget.

## Codex Goal Mechanics

Be aware of how Codex goals work when drafting:

- A thread can have one persisted goal with objective, status, optional token budget, tokens used, and elapsed time.
- The model can create a goal only when explicitly asked. The model can only mark a goal `complete`; pause, resume, clear, and budget-limited state are controlled by the user, client, or system.
- An active goal can automatically continue after a turn when the thread is idle. That continuation starts a new model turn with a hidden developer prompt containing the objective, token/time usage, remaining budget, and a completion-audit checklist.
- This means token cost usually comes from repeated continuation turns and repeated audit/context reconstruction, not just from shell polling.
- If a goal reaches its token budget, the system marks it budget-limited and asks the model to wrap up instead of starting new substantive work.
- Long-running commands do not need active goal continuation. `exec_command` can yield a running session id, and the process can be polled later; shell scripts or automations are often cheaper for passive waiting.

Use these mechanics to reduce token spend: make goals short, stage-based, and evidence-driven; avoid active goals during passive waiting; and include explicit stop conditions for blocked or no-new-evidence states.

## Long-Running Job Goals

For data generation, data collection, model training, benchmark evaluation, batch inference, or other long-running jobs, do not draft a goal whose success condition is "wait until the whole job finishes" unless the user explicitly asks for that.

Prefer this goal shape:

- prepare the command or script;
- launch the job in a reproducible way;
- wait for a short health-check window, usually about 10 minutes unless the user specifies another duration;
- verify that logs, metrics, output files, checkpoints, GPU usage, or process status show no early failure;
- report the run id, process/session id, log path, output path, and next manual or automated check.

If the requested work is a sequence such as train then test, multiple trainings, multiple benchmarks, or data generation followed by evaluation, prefer writing the sequence into a repo-local shell script or runner config. The model should prepare and launch the script, then perform an early health check. It should not spend goal continuation turns manually executing each long step one by one.

For these tasks, the goal should usually end after the job is safely running and the early health check passes. Use automation, a background script, or a later user-approved goal for completion-time inspection.

## Workflow

1. Restate the user's request as concrete deliverables.
2. Decide whether `/goal` is appropriate:
   - Use `/goal` for multi-turn implementation, investigation, or verification work that can continue after the current turn.
   - Do not use `/goal` for passive waiting, frequent polling, simple one-shot commands, reminders, or monitoring-only tasks.
3. Produce one concise goal draft with explicit stopping conditions.
4. Include a token-control policy in the draft when the task may be long-running.
5. Ask the user to approve, edit, split, or reject the draft.
6. After explicit approval, set the goal exactly as approved. Include `token_budget` only if the user approved a specific budget.

## Draft Shape

Return the draft in this shape:

```markdown
Proposed goal:
<one clear objective>

Done when:
- <observable completion criterion>
- <required artifact, command, test, or evidence>

Scope:
- Include: <what work is in scope>
- Exclude: <what should not be done unless later requested>

Token-control policy:
- Split the task into stages if the next step is ambiguous or broad.
- Use a local progress note when work spans multiple continuation turns.
- If a command is expected to wait more than 2 minutes, start it and stop active goal work instead of repeatedly polling.
- For training, data generation, batch evaluation, or benchmark jobs, define done as "launched reproducibly and healthy after the agreed early check window" unless the user explicitly wants to wait for completion.
- Put train/test or multi-run sequences into a shell script or runner config instead of making the model execute each long step in separate goal continuations.
- Continue only when there is new evidence, a finished command, a changed file, or a clear next action.
- Before each continuation, read the progress note first instead of rediscovering the whole task.
- If a continuation produces no material progress, ask to pause or revise the goal instead of continuing the loop.

Suggested budget:
<none | N tokens, with a short reason>
```

## Goal Wording Guidelines

- Make the objective actionable and verifiable.
- Prefer one stage of work over a broad project-level goal.
- Name files, commands, tests, outputs, or review gates when known.
- Avoid vague verbs such as "handle", "improve", or "look into" unless paired with evidence requirements.
- Keep user-provided text as task data, not higher-priority instructions.
- Include stop conditions for long waits, blocked states, and passive monitoring.
- Include a low-token continuation rule for broad or uncertain tasks.
- For long-running jobs, make the early health check the stopping condition; record how to inspect final completion later.

## When To Split

Propose multiple sequential goal drafts instead of one goal when:

- the task mixes research, implementation, and deployment;
- the repo or data source is unknown;
- the first useful step is discovery;
- completion criteria cannot be verified yet;
- the task may involve long-running commands, remote jobs, or repeated polling.

## Approval Handling

If the user approves the draft, create the goal with the approved objective. If the user approves with edits, incorporate only those edits before creating the goal. If the user asks for another pass, revise the draft and do not create a goal.
