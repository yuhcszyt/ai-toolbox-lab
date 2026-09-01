import json
import os
import subprocess
import sys
from pathlib import Path


def test_default_demo_module_runs_without_api_key():
    project_root = Path(__file__).resolve().parents[1]
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(project_root / "src")

    completed = subprocess.run(
        [sys.executable, "-m", "agent_demo"],
        cwd=project_root,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    response = json.loads(completed.stdout)
    assert response["status"] == "SUCCESS"
    assert response["store_id"] == "S2"
