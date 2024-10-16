"""
Discover tmt plugin.

This module provides the `discover.how=cmake` plugin.
"""

from __future__ import annotations

import dataclasses

import tmt
import tmt.utils
from tmt.steps.discover import DiscoverPlugin, DiscoverStepData

import tmt_cmake.prepare

__all__ = [
    "DiscoverCMake",
]


@dataclasses.dataclass
class DiscoverCMakeData(DiscoverStepData):
    pass


@tmt.steps.provides_method("cmake")
class DiscoverCMake(DiscoverPlugin[DiscoverCMakeData]):
    """
    Find all ctest tests.

    Must contain a prepare CMake step.
    """

    _data_class = DiscoverCMakeData

    def _check(self) -> bool:
        """Check that the discover step is well configured."""
        successful = True
        # Check that there is a prepare CMake step
        # TODO: tmt does not have a cleaner way to check the plugin type
        cmake_data = [
            data
            for data in self.step.plan.prepare.data
            if isinstance(data, tmt_cmake.prepare.PrepareCMakeData)
        ]
        if not cmake_data:
            self.fail("No CMake prepare step found")
            successful = False
        return successful

    def show(self, keys: list[str] | None = None) -> None:  # noqa: D102
        super().show(keys)
        self._check()

    def wake(self) -> None:  # noqa: D102
        super().wake()
        if not self._check():
            msg = f"Plan {self.step.plan} is not a valid CMake plan"
            raise tmt.utils.GeneralError(msg)

    def tests(  # noqa: D102
        self,
        *,
        phase_name: str | None = None,
        enabled: bool | None = None,
    ) -> list[tmt.Test]:
        raise NotImplementedError

    def go(self) -> None:  # noqa: D102
        super().go()
