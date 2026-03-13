import subprocess
import json


def test_agent_output():
    result = subprocess.run(
        ["uv", "run", "agent.py", "What is REST?"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    data = json.loads(result.stdout)

    assert "answer" in data
    assert "tool_calls" in data