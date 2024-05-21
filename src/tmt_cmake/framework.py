"""
Test framework tmt plugin.

This module provides the `framwork=cmake` plugin.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import tmt
from tmt.frameworks import TestFramework, provides_framework
from tmt.steps.execute import TEST_OUTPUT_FILENAME

from .cmake import CTestTest

if TYPE_CHECKING:
    from tmt.steps.execute import TestInvocation

__all__ = [
    "CMake",
]

CTEST_EXIT_CODES = {
    0: tmt.result.ResultOutcome.PASS,
}


@provides_framework("cmake")
class CMake(TestFramework):
    """
    Execute the actual ctests.

    Must be defined by a DiscoverCMake step.
    """

    @classmethod
    def extract_results(  # noqa: D102
        cls,
        invocation: TestInvocation,
        logger: tmt.log.Logger,  # noqa: ARG003
    ) -> list[tmt.result.Result]:
        assert invocation.return_code is not None
        result = CTEST_EXIT_CODES.get(
            invocation.return_code,
            tmt.result.ResultOutcome.FAIL,
        )
        return [
            tmt.Result.from_test_invocation(
                invocation=invocation,
                result=result,
                log=[invocation.relative_path / TEST_OUTPUT_FILENAME],
            ),
        ]

    @classmethod
    def get_test_command(  # noqa: D102
        cls,
        invocation: TestInvocation,
        logger: tmt.log.Logger,  # noqa: ARG003
    ) -> tmt.utils.ShellScript:
        assert isinstance(invocation.test, CTestTest)
        assert invocation.test._discover is not None  # noqa: SLF001
        test_command = invocation.test._discover.cmake.test(*invocation.test.ctest_args)  # noqa: SLF001
        return test_command.to_script()
