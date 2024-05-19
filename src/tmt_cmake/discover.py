"""
Discover tmt plugin.

This module provides the `discover.how=cmake` plugin.
"""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

import tmt
import tmt.utils
from tmt.steps.discover import DiscoverPlugin, DiscoverStepData
from tmt.utils import field

import tmt_cmake.prepare

if TYPE_CHECKING:
    from .prepare import PrepareCMake

__all__ = [
    "DiscoverCMake",
]


@dataclasses.dataclass
class DiscoverCMakeData(DiscoverStepData):
    @property
    def is_bare(self) -> bool:
        # Workaround for https://github.com/teemtee/tmt/issues/2827
        return False

    # CTest filters
    tests_include: str | None = field(
        option=("-R", "--tests-regex"),
        default=None,
        metavar="regex",
        help="Regex for tests to include",
    )
    tests_exclude: str | None = field(
        option=("-E", "--exclude-regex"),
        default=None,
        metavar="regex",
        help="Regex for tests to exclude",
    )
    labels_include: str | None = field(
        option=("-L", "--label-regex"),
        default=None,
        metavar="regex",
        help="Regex for test labels to include",
    )
    labels_exclude: str | None = field(
        option=("-LE", "--label-exclude"),
        default=None,
        metavar="regex",
        help="Regex for test labels to exclude",
    )


@tmt.steps.provides_method("cmake")
class DiscoverCMake(DiscoverPlugin[DiscoverCMakeData]):
    """
    Find all ctest tests.

    Must contain a prepare CMake step.
    """

    _data_class = DiscoverCMakeData
    prepare: PrepareCMake | None = None

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
        # Tests will be created after prepare step
        self.step.plan.discover.extract_tests_later = True
        self.info("Tests will be discovered after prepare.cmake step is done")
        prepare_plugins = self.step.plan.prepare.phases(tmt_cmake.prepare.PrepareCMake)
        assert len(prepare_plugins) == 1
        self.prepare = prepare_plugins[0]
        self.prepare.discover = self
