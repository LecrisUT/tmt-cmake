"""
Prepare tmt plugin.

This module provides the `prepare.how=cmake` plugin.
"""

from __future__ import annotations

import dataclasses

import tmt
from tmt.steps.prepare import PreparePlugin, PrepareStepData
from tmt.utils import Path, field

from .cmake import CMake

__all__ = [
    "PrepareCMake",
]


@dataclasses.dataclass
class PrepareCMakeData(PrepareStepData):
    # TODO: Add better attrs validator and help message
    # Main configure parameters
    build_dir: Path = field(
        option=("-B", "--build-dir"),
        default=Path("build"),
        metavar="PATH",
        help="Path to CMake project",
    )
    source_dir: Path = field(
        option=("-S", "--source-dir"),
        default=Path("."),
        metavar="PATH",
        help="Path to CMake project source",
    )
    preset: str | None = field(
        option=("-p", "--preset"),
        default=None,
        metavar="PRESET",
        help="Configure preset",
    )
    # Control the workflow
    cmake_exe: Path | None = field(
        option="--cmake-exe",
        default=None,
        metavar="PATH",
        help="Path to CMake executable. [Default: cmake in PATH]",
        show_default=False,
    )
    no_build: bool = field(
        option="--no-build",
        is_flag=True,
        default=False,
        help="Do not build or install, only configure",
    )
    install_prefix: Path | None = field(
        option="--install-prefix",
        default=None,
        metavar="PATH",
        help="Install prefix (relative to TMT_PLAN_DATA)",
    )


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
        workdir = self.step.plan.worktree
        assert workdir is not None
        plan_data_dir = self.step.plan.data_directory
        install_prefix = (
            plan_data_dir / self.data.install_prefix
            if self.data.install_prefix
            else None
        )
        # Get the CMake wrapper to execute commands
        cmake = CMake(
            source_dir=workdir / self.data.source_dir,
            build_dir=plan_data_dir / self.data.build_dir,
            cmake_exe=self.data.cmake_exe,
        )

        guest.execute(
            command=cmake.configure(
                preset=self.data.preset,
                install_prefix=install_prefix,
            ),
            env=environment,
        )
        # Double negation, if not no_build -> if build
        if not self.data.no_build:
            guest.execute(
                command=cmake.build(),
                env=environment,
            )
            # Run install only if install_prefix was specified
            if self.data.install_prefix:
                guest.execute(
                    command=cmake.install(),
                    env=environment,
                )
