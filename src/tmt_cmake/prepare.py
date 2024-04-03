"""
Prepare tmt plugin.

This module provides the `prepare.how=cmake` plugin.
"""

from __future__ import annotations

import dataclasses

import tmt
from tmt.steps.prepare import PreparePlugin, PrepareStepData

__all__ = [
    "PrepareCMake",
]


@dataclasses.dataclass
class PrepareCMakeData(PrepareStepData):
    pass


@tmt.steps.provides_method("cmake")
class PrepareCMake(PreparePlugin[PrepareCMakeData]):
    """
    Configure (and build) a CMake project.

    Currently requires having a configure preset.
    """

    _data_class = PrepareCMakeData

    def _check(self) -> bool:
        """Check that the prepare step is well configured."""
        successful = True
        # Check that there is no other prepare step of type CMake
        # TODO: tmt does not have a cleaner way to check the plugin type
        cmake_data = [
            data
            for data in self.step.plan.prepare.data
            if isinstance(data, PrepareCMakeData)
        ]
        if len(cmake_data) > 1:
            self.fail("More than one CMake prepare step was specified")
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

    def go(  # noqa: D102
        self,
        *,
        guest: tmt.steps.provision.Guest,
        environment: tmt.utils.Environment | None = None,
        logger: tmt.log.Logger,
    ) -> None:
        super().go(guest=guest, environment=environment, logger=logger)
        # TODO: Implement CMake configure step
