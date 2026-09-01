# ai-toolbox-lab

Python experiments and deterministic AI-agent runtime examples.

## Contents

- `JSONSchemaDemo/` — offline agent runtime demo with deterministic tests.
- `invoke1.py` — LangChain structured-output example using the local `.env` configuration.
- `main.py` — small Python smoke script.
- `yu-dev-flow-v7/` — workflow skill reference package.

## Verify

```powershell
.\.venv\Scripts\python.exe -m pytest JSONSchemaDemo -q
.\.venv\Scripts\python.exe -m unittest test_invoke1.py
```

Keep credentials in the local `.env` file; it is intentionally excluded from Git.
