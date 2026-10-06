"""Offline smoke checks; does not call a model or inspect task answers."""

import os
import tempfile
from pathlib import Path

from lab.agent import make_backend


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="lab-shell-check-") as folder:
        previous = os.environ.get("LAB_API_KEY")
        os.environ["LAB_API_KEY"] = "runtime-check-secret-sentinel"
        try:
            backend = make_backend(Path(folder))
        finally:
            if previous is None:
                os.environ.pop("LAB_API_KEY", None)
            else:
                os.environ["LAB_API_KEY"] = previous
        commands = [
            "python -m pytest --version",
            "python - <<'PY'\nimport sys, socket, asyncio\nprint(sys.version.split()[0])\nprint('HEREDOC_OK')\nPY",
            "python -c \"print('pipe_ok')\" | tr a-z A-Z",
        ]
        for command in commands:
            result = backend.execute(command)
            print(f"exit={result.exit_code}: {result.output.strip()}")
            assert result.exit_code == 0
        output = backend.execute("env").output
        assert "runtime-check-secret-sentinel" not in output
        print("SECRET_FILTER_OK")
        try:
            backend.execute("true", timeout=0)
        except ValueError:
            print("TIMEOUT_VALIDATION_OK")
        else:
            raise AssertionError("timeout=0 was accepted")


if __name__ == "__main__":
    main()
