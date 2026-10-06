---
name: maintain-test-integrity
description: Use this skill when adding or modifying tests to ensure original test files remain unmodified and regression tests are properly added.
---
- Never modify existing test files in the tests/ directory.
- Add new test files for new tests or regression tests.
- Create a dedicated regression test file (e.g., tests/test_regressions.py).
- Add one test function per fixed bug in the regression test file.
- Ensure all new tests pass without errors or failures.
- Run the full test suite to confirm no regressions.
- Follow naming conventions and test discovery patterns.
- Confirm test files are included in test discovery commands.
- Avoid changing test fixtures or setup unless necessary and documented.
