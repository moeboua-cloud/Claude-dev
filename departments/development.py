"""
DEVELOPMENT department
  - CLAWD    — Senior Developer  (full-stack development, code review)
  - SENTINEL — QA Monitor        (system monitoring, QA testing)
"""

from __future__ import annotations
import subprocess
from agents.base import Agent, STRONG_MODEL, FAST_MODEL
from tools.definitions import CODE_EXECUTION_TOOL, RUN_TESTS_TOOL


class Clawd(Agent):
    """
    CLAWD — Senior Developer

    Speciality: Full-stack development and code review. CLAWD writes clean,
    production-ready code, reviews PRs, and can execute code to validate logic.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CLAWD",
            system_prompt=(
                "You are CLAWD, a Senior Full-Stack Developer. "
                "You write clean, well-documented, production-ready code. "
                "Your process:\n"
                "1. Understand requirements before writing a single line.\n"
                "2. Use code_execution to test and validate your implementations.\n"
                "3. Follow best practices: SOLID principles, error handling, tests.\n"
                "4. During code reviews: check security, performance, maintainability.\n\n"
                "Output format: code blocks with language tags + explanation."
            ),
            tools=[CODE_EXECUTION_TOOL],
            model=STRONG_MODEL,
        )


class Sentinel(Agent):
    """
    SENTINEL — QA Monitor

    Speciality: System monitoring and automated QA testing. SENTINEL ensures
    quality gates are maintained and catches regressions early.
    """

    def __init__(self) -> None:
        super().__init__(
            name="SENTINEL",
            system_prompt=(
                "You are SENTINEL, a QA Monitor responsible for software quality. "
                "Your mission: zero regressions reach production. "
                "You:\n"
                "1. Design and run comprehensive test suites.\n"
                "2. Analyse test results and identify failure patterns.\n"
                "3. Use run_tests to execute the test suite.\n"
                "4. Use code_execution to reproduce and debug failures.\n\n"
                "Output: Test Report with pass/fail counts, coverage %, and "
                "a prioritised list of issues."
            ),
            tools=[RUN_TESTS_TOOL, CODE_EXECUTION_TOOL],
            model=FAST_MODEL,
        )

    def _execute_tool(self, name: str, input_data: dict):
        if name == "run_tests":
            module = input_data.get("module", "all")
            # In production: subprocess.run(["pytest", module, "--tb=short"])
            return {
                "module": module,
                "passed": 47,
                "failed": 2,
                "errors": 0,
                "coverage": "84%",
                "failures": [
                    {"test": "test_auth_timeout", "reason": "Timeout after 5s"},
                    {"test": "test_payment_retry", "reason": "AssertionError: expected 3 retries, got 2"},
                ],
            }
        return super()._execute_tool(name, input_data)
