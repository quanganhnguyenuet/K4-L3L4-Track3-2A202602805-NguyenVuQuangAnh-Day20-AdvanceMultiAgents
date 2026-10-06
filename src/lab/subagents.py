"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": (
                "Use when the task needs repository exploration, inspection of files or data, "
                "or a factual report before any changes are made. Do not modify files."
            ),
            "system_prompt": (
                "You are an exploration specialist. Inspect the relevant files and evidence, "
                "check assumptions, and return a concise factual report. Do not modify files."
            ),
        },
        {
            "name": "implementer",
            "description": (
                "Use when the task requires implementing or repairing code, running focused tests, "
                "and reporting exactly what changed."
            ),
            "system_prompt": (
                "You are an implementation specialist. Make the requested changes carefully, "
                "run relevant tests, and report the files changed and the verification results."
            ),
        },
        {
            "name": "reviewer",
            "description": (
                "Use when an independent review is needed to check correctness, requirements, "
                "regressions, and edge cases without changing the implementation."
            ),
            "system_prompt": (
                "You are an independent reviewer. Inspect the implementation against the task "
                "requirements, look for defects and edge cases, and return findings with evidence. "
                "Do not modify files."
            ),
        },
    ]
