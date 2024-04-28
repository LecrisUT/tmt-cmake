from __future__ import annotations

import inspect
from importlib.metadata import version
from typing import TYPE_CHECKING

import pytest
import tmt_cmake
import tmt_cmake.discover
import tmt_cmake.prepare

if TYPE_CHECKING:
    import tmt.utils
    from pytest_check.context_manager import CheckContextManager


@pytest.mark.parametrize(
    ("tmt_command", "plugin"),
    [
        (
            ["run", "prepare", "--how=cmake", "--help"],
            tmt_cmake.prepare.PrepareCMake,
        ),
        (
            ["run", "discover", "--how=cmake", "--help"],
            tmt_cmake.discover.DiscoverCMake,
        ),
    ],
)
def test_help(
    check: CheckContextManager,
    tmt_cli,
    tmt_command: list[str],
    plugin: tmt.utils.Common,
) -> None:
    """Check that the plugins are found in the help messages."""
    result = tmt_cli(tmt_command)
    check.equal(result.exit_code, 0)
    doc_string = inspect.getdoc(plugin)
    assert doc_string is not None  # narrow type
    for line in doc_string.splitlines():
        check.is_in(line, result.stdout)


def test_version() -> None:
    """Check that the package version is defined and consistent."""
    assert tmt_cmake.__version__ == version("tmt-cmake")
