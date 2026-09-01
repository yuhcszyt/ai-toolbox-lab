# Bundled Matt skill dependencies

These skill folders are snapshots copied from the user's installed Matt skills under `C:\Users\Administrator\.agents\skills` on 2026-09-01. The copied `SKILL.md`, `agents/openai.yaml`, and supporting files are the local source bundled with this versioned package; the older flat `matt/*.md` files are not part of the handoff path.

## Route stages

The router can hand off to these bundled stages:

- `grill-with-docs`
- `to-spec`
- `to-tickets`
- `implement`
- `wayfinder`
- `setup-matt-pocock-skills` (only when a selected stage needs missing repo configuration)

## Transitive closure

| Skill | Bundled dependencies |
| --- | --- |
| `grill-with-docs` | `grilling`, `domain-modeling` |
| `wayfinder` | `grilling`, `domain-modeling`, `research`, `prototype` |
| `implement` | `tdd`, `code-review` |
| `tdd` | `codebase-design` (when interface shape is under question) |
| `triage` | `grilling`, `domain-modeling` (when triage needs clarification) |
| `setup-matt-pocock-skills` | its issue-tracker/domain/triage templates; `triage` is bundled so label setup remains complete |
| `to-spec`, `to-tickets` | `setup-matt-pocock-skills` repo configuration |

Each dependency is copied as a complete skill directory, including any linked references:

- `domain-modeling`: `CONTEXT-FORMAT.md`, `ADR-FORMAT.md`
- `codebase-design`: `DEEPENING.md`, `DESIGN-IT-TWICE.md`
- `prototype`: `LOGIC.md`, `UI.md`
- `tdd`: `tests.md`, `mocking.md`
- `triage`: `AGENT-BRIEF.md`, `OUT-OF-SCOPE.md`
- `setup-matt-pocock-skills`: issue-tracker templates, `domain.md`, and `triage-labels.md`

When a handoff names a stage, invoke the current skill name (`/<stage>`) only when the host permits that explicit handoff. The bundled files provide dependency references for this package.
