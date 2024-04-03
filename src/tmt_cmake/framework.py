"""
Test framework tmt plugin.

This module provides the `framwork=cmake` plugin.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tmt.frameworks import TestFramework, provides_framework

if TYPE_CHECKING:
    import tmt
    from tmt.steps.execute import TestInvocation

__all__ = [
    "CMake",
]


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
        logger: tmt.log.Logger,
    ) -> list[tmt.result.Result]:
        raise NotImplementedError

    @classmethod
    def get_test_command(  # noqa: D102
        cls,
        invocation: TestInvocation,
        logger: tmt.log.Logger,
    ) -> tmt.utils.ShellScript:
        raise NotImplementedError
