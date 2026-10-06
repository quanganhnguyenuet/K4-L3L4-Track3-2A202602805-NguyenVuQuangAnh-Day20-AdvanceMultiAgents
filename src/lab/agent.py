"""Build the Deep Agents used by the lab."""

import os
import sys
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import LocalShellBackend

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
    else:
        path_entries.extend(["/usr/local/bin", "/usr/bin", "/bin"])
    env = {
        "PATH": os.pathsep.join(path_entries),
        "HOME": str(Path(sandbox).resolve()),
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    return LocalShellBackend(
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
