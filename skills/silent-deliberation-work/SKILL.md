---
name: silent-deliberation-work
description: Quiet deliberation mode for tasks that require silent work, first-principles reasoning, adaptive strategies, and worst-case guarantees. Use when the user asks for "静默沉思工作", silent deliberation, no optional commentary/progress updates, final-only answers, or quantitative/logical/boundary guarantee problems needing sufficiency and lower-bound proofs.
---

# 静默沉思工作

Use this skill to solve the user's task with minimal visible chatter and explicit guarantee-oriented reasoning in the final answer.

## Interaction Mode

- Do not send optional commentary, progress narration, status updates, or intermediate explanations.
- Use commentary only when a tool call requires it or when the user explicitly asks for status.
- For tasks that need no tools, reason first and answer only in `final`.
- Do not reveal private scratch work. Include only the reasoning needed to justify the result.
- If a higher-priority instruction requires a visible update, keep it as short and factual as possible.

## Reasoning Procedure

Before solving, identify:

- What information is observable.
- What actions or choices are controllable.
- What guarantee the answer must provide.

Then solve from first principles:

- Prefer derivation from constraints over pattern matching or remembered puzzle templates.
- If an attribute can be observed, touched, marked, ordered, compared, or otherwise controlled, use a staged or adaptive strategy that exploits that control.
- Do not reduce a controllable problem to blind one-shot sampling unless no adaptive information can be gained.
- Keep the method general. Do not tailor the reasoning to a specific benchmark, expected answer, or hidden test.

## Guarantees and Bounds

For quantitative, logical, boundary, adversarial, or guarantee-style tasks:

- Prove the proposed strategy is sufficient in the worst case.
- Prove a matching lower bound when the problem asks for a minimum, optimum, or guarantee.
- If a matching lower bound is not applicable, say why briefly.
- Recheck arithmetic and make sure any final number answers the exact question.

## Final Answer Shape

Use the shortest structure that fully supports the answer:

1. State the strategy or key idea.
2. Give the worst-case sufficiency proof.
3. Give the lower-bound proof when applicable.
4. State the final answer clearly.
