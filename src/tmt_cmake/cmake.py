"""CMake commands and utilities."""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

import attrs
from tmt import Test
from tmt.utils import Command, Path, field

if TYPE_CHECKING:
    from typing import Any

    import fmf
    import tmt
    from tmt.steps import BasePlugin, StepDataT

    from .discover import DiscoverCMake
    from .prepare import PrepareCMakeData


def _convert_cmake_exe(val: Path | None) -> Path | str:
    # No converter decorator yet
    # https://github.com/python-attrs/attrs/pull/404
    return val if val else "cmake"


def _convert_ctest_exe(val: Path | None) -> Path | str:
    # No converter decorator yet
    # https://github.com/python-attrs/attrs/pull/404
    return val if val else "ctest"


@attrs.define
class CMake:
    """
    CMake execution wrapper.

    Provides tmt commands for
    """

    source_dir: Path
    """Project's source path"""
    build_dir: Path
    """Project's build path"""
    cmake_exe: Path | str = attrs.field(converter=_convert_cmake_exe)
    """CMake executable to use [default search from ``PATH``]"""
    ctest_exe: Path | str = attrs.field(converter=_convert_ctest_exe)
    """CTest executable to use [default search from ``PATH``]"""

    @classmethod
    def from_prepare_data(
        cls,
        data: PrepareCMakeData,
        plugin: BasePlugin[StepDataT],
        ctest_exe: Path | None = None,
    ) -> CMake:
        """
        Construct CMake wrapper from Prepare plugin data.

        :param data: Prepare plugin data
        :param plugin: Base plugin (can be from any step)
        :param ctest_exe: Path to ctest defined in discover stage
        :return: CMake wrapper
        """
        workdir = plugin.step.plan.worktree
        assert workdir is not None
        plan_data_dir = plugin.step.plan.data_directory
        return CMake(
            source_dir=workdir / data.source_dir,
            build_dir=plan_data_dir / data.build_dir,
            cmake_exe=data.cmake_exe,
            ctest_exe=ctest_exe,
        )

    def configure(
        self,
        preset: str | None = None,
        install_prefix: Path | None = None,
        defines: dict[str, str] | None = None,
    ) -> Command:
        """
        CMake configure command.

        :param preset: Project's preset to configure
        :param install_prefix: Install prefix
        :param defines: Dict of CMake cache variables to define
        :return: tmt command to run
        """
        cmake_args = [
            f"-S{self.source_dir}",
            f"-B{self.build_dir}",
        ]
        if preset:
            cmake_args.append(f"--preset={preset}")
        if install_prefix:
            cmake_args.append(f"--install-prefix={install_prefix}")
        if defines:
            for var, value in defines.items():
                cmake_args.append(f"-D{var}={value}")
        return Command(self.cmake_exe, *cmake_args)

    def build(self) -> Command:
        """
        CMake build command.

        :return: tmt command to run
        """
        cmake_args = [
            "--build",
            str(self.build_dir),
        ]
        return Command(self.cmake_exe, *cmake_args)

    def install(self) -> Command:
        """
        CMake install command.

        :return: tmt command to run
        """
        cmake_args = [
            "--install",
            str(self.build_dir),
        ]
        return Command(self.cmake_exe, *cmake_args)

    def test(self, *args: str) -> Command:
        """
        CTest command.

        :return: tmt command to run
        """
        cmake_args = [
            "--test-dir",
            str(self.build_dir),
            *args,
        ]
        return Command(self.ctest_exe, *cmake_args)


@dataclasses.dataclass
class CTestTest(Test):
    """CTest specific test type."""

    # _discover is prefixed with _ so that it doesn't get used for saving the data
    _discover: DiscoverCMake | None = None
    """Discover phase that consturcted the test"""
    ctest_args: list[str] = field(
        default_factory=list,
    )
    """CTest arguments to execute"""

    def __init__(  # noqa: D107, PLR0913
        self,
        *,
        node: fmf.Tree,
        tree: tmt.Tree | None = None,
        skip_validation: bool = False,
        raise_on_validation_error: bool = False,
        logger: tmt.log.Logger,
        discover: DiscoverCMake,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        super().__init__(
            node=node,
            tree=tree,
            skip_validation=skip_validation,
            raise_on_validation_error=raise_on_validation_error,
            logger=logger,
            **kwargs,
        )
        self._discover = discover
        self.ctest_args = node["ctest_args"]
