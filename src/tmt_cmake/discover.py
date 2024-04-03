"""
Discover tmt plugin.

This module provides the `discover.how=cmake` plugin.
"""

from __future__ import annotations

import dataclasses

import tmt
from tmt.steps.discover import DiscoverPlugin, DiscoverStepData

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

    def tests(  # noqa: D102
        self,
        *,
        phase_name: str | None = None,
        enabled: bool | None = None,
    ) -> list[tmt.Test]:
        raise NotImplementedError

    def go(self) -> None:  # noqa: D102
        super().go()
