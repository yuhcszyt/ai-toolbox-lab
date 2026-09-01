# Repository Guidelines

## Project Structure & Module Organization

- `invoke1.py` is a LangChain/OpenAI structured-output example; `main.py` is a small smoke script, and `test_invoke1.py` contains mocked `unittest` coverage.
- `JSONSchemaDemo/src/agent_demo/` is the offline Python 3.12+ Agent Runtime, organized into `agent`, `llm`, `tools`, `services`, `repositories`, `dto`, `validation`, and `observability` layers. Its tests live in `JSONSchemaDemo/tests/`, with the design specification in `JSONSchemaDemo/doc/`.
- `yu-dev-flow-v7/` contains workflow reference material. Keep credentials in the local `.env` file; no committed asset directory is required.

## Build, Test, and Development Commands

Use the repository virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pytest JSONSchemaDemo -q
Set-Location JSONSchemaDemo
$env:PYTHONPATH = "$PWD\src"
..\.venv\Scripts\python.exe -m agent_demo
```

Install the demo package when needed with `..\.venv\Scripts\python.exe -m pip install -e . --no-deps`. Run `invoke1.py` only when `.env` provides `API_KEY`, `BASE_URL`, and `MODEL`, because it contacts the configured model service.

## Coding Style & Naming Conventions

Target Python 3.12+, use four-space indentation, type hints, async APIs, and Pydantic v2 models. Use `snake_case` for modules, functions, and variables; `PascalCase` for classes and models; and `test_*.py` / `test_*` for tests. No repository formatter or linter is configured, so preserve nearby style and explicit layer boundaries.

## Testing Guidelines

Prefer deterministic pytest scenarios under `JSONSchemaDemo/tests/` using `FakeLLM` and in-memory repositories; do not require network access or API keys. Cover behavior and guardrails such as timeouts, retries, evidence/business validation, and call budgets. Keep root-script tests mocked and in `unittest` style.

## Commit & Pull Request Guidelines

No Git history or PR template is present, so use concise imperative messages such as `Add ...` or `Fix ...`. After every completed task and passing verification, commit and push the changes to GitHub:

```powershell
git add <files>
git commit -m "Describe the change"
git push origin <branch>
```

Verify the remote and branch first, keep `.env` and secrets out of commits, and report a missing remote or any task-specific version-control restriction instead of guessing.

## Architecture & Safety Notes

Read `JSONSchemaDemo/doc/agent-loop-demo-spec.md` before changing the demo. Keep LLM decisions separate from runtime guardrails, evidence/business validation, and trusted response construction; never return raw model JSON or expose credentials.
