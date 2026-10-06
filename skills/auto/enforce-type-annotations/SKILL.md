---
name: enforce-type-annotations
description: Use this skill when adding or reviewing public functions to ensure all parameters and return values have explicit type annotations.
---
- Identify all public functions (names not starting with '_') in the codebase.
- For each public function, verify every parameter has a type annotation.
- Verify the return type annotation is present.
- If any annotation is missing, add the appropriate type hint based on the function’s logic or documentation.
- Use consistent style for type hints (e.g., PEP 484).
- Run static type checkers (e.g., mypy) to confirm no missing or incorrect annotations.
- Document any assumptions or complex types in docstrings if needed.
