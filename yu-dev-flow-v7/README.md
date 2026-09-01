# yu-dev-flow

`yu-dev-flow` routes authorized code changes through the smallest sufficient L0-L3 workflow.

- `SKILL.md` is the concise router and conditional setup gate.
- `routes/l0.md` through `routes/l3.md` contain level-specific handoff rules.
- `matt/<skill>/` contains bundled dependency references; the router invokes each stage skill by name and carries its handoff contract.
- `implement` owns code changes, tests, validation, and review.

The bundled dependency closure is documented in [`matt/DEPENDENCIES.md`](matt/DEPENDENCIES.md). It was copied from the installed Matt skills under the user's `.agents/skills` directory, so the router no longer depends on the older flat `matt/*.md` references.

Users do not need to initialize `yu-dev-flow`. The router checks for repo-local Matt configuration only when a selected route requires it, then invokes `/setup-matt-pocock-skills` if that configuration is missing.
