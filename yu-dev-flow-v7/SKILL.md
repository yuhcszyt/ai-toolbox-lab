---
name: yu-dev-flow
description: Route authorized code changes through the smallest sufficient L0-L3 workflow, conditionally hand off workflow skills, and carry minimum-code constraints into implementation. Use for implement, fix, refactor, migrate, or modify requests; not explanation-only, diagnosis-only, review-only, or design-only requests.
---

# yu-dev-flow

You are the workflow router for authorized code changes. Choose the lowest sufficient route, read only the matching route reference, and hand off in order. Do not ask the user to choose L0-L3 or a workflow name.

`routes/l0.md` through `routes/l3.md` contain level-specific rules. At each handoff, invoke the named skill (for example, `/implement`) with the handoff contract. `matt/DEPENDENCIES.md` records the bundled dependency closure; consult it when adding or changing a handoff dependency.

## Scope and authorization

- Enter L0-L3 only when the user authorizes a code change.
- For explanation-only, diagnosis-only, review-only, or design-only requests, do not schedule implementation or setup.
- Treat explicit limits such as “do not change code”, “do not run tests”, or a restricted file/module/tool scope as hard constraints.
- Do not treat a workflow stage as extra authorization. Keep version control read-only unless the user explicitly requests a VCS mutation.

## Select a route

Use project evidence and decision complexity, not file count, line count, or task size. Read more evidence when the level is unclear. Evaluate in order and stop at the first match:

| Level | Match when | Handoff | Setup gate |
| --- | --- | --- | --- |
| **L0 Direct** | Goal, rules, scope, and an existing pattern are clear; no blocker remains. | `implement` | None |
| **L1 Clarify** | A small blocking uncertainty can be resolved without fixing a shared contract. | `grill-with-docs` → `implement` | None; promote if a contract appears |
| **L2 Contract** | An API, data, state, transaction, module responsibility, or several business rules must be fixed as a contract. | `grill-with-docs` → `to-spec` → `implement` | `to-spec` needs issue-tracker and triage-label configuration |
| **L3 Coordinate** | At least two independently deliverable slices need real dependency, handoff, or context coordination. | `wayfinder`, or `grill-with-docs` → `to-spec` → `to-tickets` → `implement` | `wayfinder` needs issue-tracker configuration; `to-spec`/`to-tickets` need both configurations |

Risk floor: unclear transaction, idempotency, concurrency, authorization, security, payment, migration, deletion, overwrite, public API, cross-service consistency, retry, or compensation semantics require at least L1. A shared contract requires L2. Use L3 only for a real dependency, handoff, or context-separation benefit.

## Read only what the route needs

1. Select the level from the table.
2. Read the matching `routes/lN.md`.
3. At each handoff, invoke only the named skill.
4. Reclassify if new evidence changes uncertainty, contract, dependency, or handoff cost. Reuse completed artifacts instead of rebuilding them.

## Conditional Matt setup

`setup-matt-pocock-skills` is not a required initialization step for using `yu-dev-flow`. It is a one-time, repo-local prerequisite only when a selected workflow skill needs configuration that is absent.

Check the repository or the current handoff context, not the installation directory:

- An issue-tracker configuration must be present in `docs/agents/issue-tracker.md` or explicitly supplied in the current context for `wayfinder`, `to-spec`, and `to-tickets`.
- A triage-label configuration must be present in `docs/agents/triage-labels.md` or explicitly supplied in the current context for `to-spec` and `to-tickets`.
- L0 and L1 do not trigger setup. An L1 route that promotes to L2/L3 reevaluates this gate.

When a required file is missing:

1. Invoke `/setup-matt-pocock-skills` as the next handoff and pause the dependent route until setup is complete.
2. Do not install skills, write the repo configuration, or claim setup ran. The source is prompt-driven and `disable-model-invocation: true`; it must present findings and obtain user confirmation before editing.
3. If the setup skill is unavailable, report the broken Skill package and keep the route blocked. Do not silently fetch or install another copy.

This conditional handoff is the only setup trigger. Never ask users to initialize `yu-dev-flow` separately.

## Handoff contract

Every handoff states only: current level, evidence/reason, next stage, existing artifacts, unresolved decisions, and the minimum-implementation constraints. A completed artifact satisfies its stage; skip that stage.

- `grill-with-docs` resolves implementation-changing decisions and records domain context.
- `wayfinder` maps decision fog that exceeds one session; it plans and does not deliver the destination.
- `to-spec` turns confirmed decisions into an implementation contract and does not re-interview the user.
- `to-tickets` turns an approved contract into independently deliverable slices with genuine blockers.
- `implement` owns code changes, tests, validation, and review.

The handoff skills retain their current explicit-only invocation policy. Invoke the named skill and output the handoff; do not claim a stage ran. If a handoff fails, report the failure and keep the route; do not simulate a result or use the failure as a reason to install/setup.

## Minimum implementation constraints

Carry these constraints into every `/implement` handoff and let that skill apply its execution procedure:

- Stop at the first sufficient solution: remove the need, reuse code, use the standard library, use a native platform feature, use an installed dependency, then write new code only when necessary.
- Prefer the fewest files and smallest correct diff. Avoid unrequested abstractions, single-use factories, speculative configuration, unnecessary dependencies, and future scaffolding.
- Never simplify away trust-boundary validation, data-loss prevention, security controls, accessibility basics, or relevant edge-case correctness.
- Non-trivial new logic leaves one minimal runnable check; trivial changes need no extra test.

## Output examples

At the start or on a route change, use one sentence and name the next handoff:

```text
The goal and boundaries are clear, so this is L0; next, hand off to implement.

Retry and idempotency semantics are missing, so this is L1; next, hand off to grill-with-docs.

This change fixes a public API and state contract, so this is L2; next, hand off to grill-with-docs, then to-spec.

This work has independent slices with dependencies, so this is L3; setup is missing, so first invoke `/setup-matt-pocock-skills`, then resume the route.
```
