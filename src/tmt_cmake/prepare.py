"""
Prepare tmt plugin.

This module provides the `prepare.how=cmake` plugin.
"""

from __future__ import annotations

import dataclasses

import tmt
from tmt.steps.prepare import PreparePlugin, PrepareStepData
from tmt.utils import field

__all__ = [
    "PrepareCMake",
]


@dataclasses.dataclass
class PrepareCMakeData(PrepareStepData):
    preset: str = field(
        option=("-p", "--preset"),
        metavar="PRESET",
        help="Configure preset",
    )


@tmt.steps.provides_method("cmake")
class PrepareCMake(PreparePlugin[PrepareCMakeData]):
    """
    Configure (and build) a CMake project.

    Currently requires having a configure preset.
    """

    _data_class = PrepareCMakeData

    def go(
        self,
        *,
        guest: tmt.steps.provision.Guest,
        environment: tmt.utils.EnvironmentType | None = None,
        logger: tmt.log.Logger,
    ) -> None:
        """Execute prepare plugin."""
        super().go(guest=guest, environment=environment, logger=logger)
        # TODO: Implement CMake configure step
