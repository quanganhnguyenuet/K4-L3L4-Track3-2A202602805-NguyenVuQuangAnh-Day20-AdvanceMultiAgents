"""Build the Deep Agents used by the lab."""

import os
import subprocess
import sys
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import LocalShellBackend
from deepagents.backends.protocol import ExecuteResponse

from .model import make_model
from .subagents import get_subagents


PATHS_NOTE = (
    "PATHS: every path is relative to the sandbox root and never starts with '/'. "
    "The task files are in the folder workspace/ (for example workspace/app.log). "
    "Use exactly this relative form both in the file tools and in the shell (execute); "
    "the shell starts in the sandbox root. "
)
BASE_PROMPT = (
    "You are an engineering assistant working in a sandbox. "
    + PATHS_NOTE
    + "Use the shell to run Python and tests. "
    "When you are done, reply with a short summary that mentions only files you really created or changed."
)
SKILLS_NOTE = (
    " Skills are in the folder skills/ (one sub-folder per skill with a SKILL.md). "
    "As your FIRST action, read the SKILL.md of every skill whose description could apply to the task, "
    "then follow them. Never modify skills/."
)
SUBAGENTS_NOTE = (
    " You have specialised subagents (see the description of the task tool). "
    "For anything beyond a trivial step, delegate to a suitable subagent and put ALL the task rules and file paths "
    "in the delegation message, because a subagent sees only what you send. "
    "Check what a subagent returns before you rely on it."
)


def make_backend(sandbox: Path):
    """Create a shell/filesystem backend rooted at ``sandbox``."""
    python_dir = str(Path(sys.executable).resolve().parent)
    path_entries = [python_dir]
    scripts_dir = Path(python_dir) / "Scripts"
    if scripts_dir.is_dir():
        path_entries.append(str(scripts_dir))
    bash_path = None
    if os.name == "nt":
        path_entries.extend([
            os.environ.get("SystemRoot", r"C:\Windows") + r"\System32",
            os.environ.get("SystemRoot", r"C:\Windows"),
        ])
        program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
        for utility_dir in (
            Path(program_files) / "Git" / "usr" / "bin",
            Path(program_files) / "Git" / "bin",
        ):
            if utility_dir.is_dir():
                path_entries.append(str(utility_dir))
        candidate = Path(program_files) / "Git" / "bin" / "bash.exe"
        if candidate.is_file():
            bash_path = candidate
    else:
        path_entries.extend(["/usr/local/bin", "/usr/bin", "/bin"])
    env = {
        "PATH": os.pathsep.join(path_entries),
        "HOME": str(Path(sandbox).resolve()),
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONUTF8": "1",
        "TEMP": str(Path(sandbox).resolve()),
        "TMP": str(Path(sandbox).resolve()),
    }
    if os.name == "nt":
        # Windows Python needs these even in an otherwise sanitized environment.
        env["SystemRoot"] = os.environ.get("SystemRoot", r"C:\Windows")
        env["WINDIR"] = env["SystemRoot"]

    class BashShellBackend(LocalShellBackend):
        """Use Git Bash on Windows for the POSIX shell advertised by execute."""

        def execute(self, command: str, *, timeout: int | None = None):
            if not isinstance(command, str) or not command:
                return ExecuteResponse(output="Error: Command must be a non-empty string.", exit_code=1, truncated=False)
            effective_timeout = self._default_timeout if timeout is None else timeout
            if effective_timeout <= 0:
                raise ValueError(f"timeout must be positive, got {effective_timeout}")
            try:
                result = subprocess.run(
                    [str(bash_path), "--noprofile", "--norc", "-c", command],
                    cwd=str(self.cwd), env=self._env, stdin=subprocess.DEVNULL,
                    capture_output=True, text=True, encoding="utf-8", errors="replace",
                    timeout=effective_timeout, check=False,
                )
                parts = [result.stdout] if result.stdout else []
                if result.stderr:
                    parts.extend(f"[stderr] {line}" for line in result.stderr.rstrip().splitlines())
                output = "\n".join(parts) or "<no output>"
                truncated = len(output) > self._max_output_bytes
                if truncated:
                    output = output[:self._max_output_bytes] + "\n... Output truncated."
                if result.returncode:
                    output += f"\nExit code: {result.returncode}"
                return ExecuteResponse(output=output, exit_code=result.returncode, truncated=truncated)
            except subprocess.TimeoutExpired:
                return ExecuteResponse(output=f"Error: Command timed out after {effective_timeout} seconds.", exit_code=124, truncated=False)
            except OSError as exc:
                return ExecuteResponse(output=f"Error executing command ({type(exc).__name__}): {exc}", exit_code=1, truncated=False)

    backend_class = BashShellBackend if bash_path is not None else LocalShellBackend
    return backend_class(
        root_dir=sandbox,
        virtual_mode=True,
        inherit_env=False,
        env=env,
        timeout=120,
    )


def build_agent(sandbox: Path, mode: str = "single", use_skills: bool = False, model=None):
    """Build a Deep Agent in either single-agent or custom-subagent mode."""
    if mode not in {"single", "subagents"}:
        raise ValueError(f"unknown mode: {mode}")

    kwargs = {}
    prompt = BASE_PROMPT
    if mode == "subagents":
        kwargs["subagents"] = [
            {
                **subagent,
                "system_prompt": subagent["system_prompt"] + " " + PATHS_NOTE,
            }
            for subagent in get_subagents()
        ]
        prompt += SUBAGENTS_NOTE
    if use_skills:
        kwargs["skills"] = ["/skills/"]
        prompt += SKILLS_NOTE

    return create_deep_agent(
        model=model if model is not None else make_model(),
        system_prompt=prompt,
        backend=make_backend(sandbox),
        **kwargs,
    )
