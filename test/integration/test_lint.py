from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pytest_check.context_manager import CheckContextManager

DATA_DIR = (Path(__file__).parent / "data" / "lint").resolve()


@pytest.mark.parametrize(
    "plan",
    [
        "/good/prepare",
        "/good/discover",
        "/full/prepare",
        "/full/discover",
    ],
)
def test_good_lint(
    check: CheckContextManager,
    tmt_cli,
    plan: str,
) -> None:
    args = [
        f"--root={DATA_DIR}",
        "lint",
        "plans",
        "--disable-check=C000",  # Disabled because JSON schema is not expandable yet
        "--disable-check=C001",  # Disabled because the plans have long summaries
        plan,
    ]
    result = tmt_cli(args)
    check.equal(result.exit_code, 0)
    # Check that there are no failing or warning lints
    for line in result.stdout.splitlines():
        check.is_false(re.match(r"(?i)^fail [a-z]\d{3}]", line))
        check.is_false(re.match(r"(?i)^warn [a-z]\d{3}]", line))
    # TODO: Use caplog to check all other messages
    # Disabled because JSON schema is not expandable
    # assert "warn" not in result.stdout


@pytest.mark.parametrize(
    ("plan", "message"),
    [
        (
            "/fail/multiple-prepare",
            "fail: More than one CMake prepare step was specified",
        ),
        (
            "/fail/discover-no-prepare",
            "fail: No CMake prepare step found",
        ),
    ],
)
def test_fail_lint(
    check: CheckContextManager,
    tmt_cli,
    plan: str,
    message: str,
) -> None:
    # TODO: Use caplog to check all other messages
    args = [
        f"--root={DATA_DIR}",
        "lint",
        "plans",
        "--disable-check=C001",  # Disabled because the plans have long summaries
        plan,
    ]
    result = tmt_cli(args)
    # TODO: For now no fail lints added, so they should pass
    check.equal(result.exit_code, 0)
    # Check that they fail on plans show though
    args = [
        f"--root={DATA_DIR}",
        "plans",
        "show",
        plan,
    ]
    result = tmt_cli(args)
    # TODO: `tmt show` should exit 1, but not sure how to do it
    check.equal(result.exit_code, 0)
    check.is_in(message, result.stdout)
