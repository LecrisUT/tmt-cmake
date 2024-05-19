"""CMake commands and utilities."""

from __future__ import annotations

import attrs
from tmt.utils import Command, Path


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
    cmake_exe: Path | str = attrs.field(default=None, converter=_convert_cmake_exe)
    """CMake executable to use [default search from ``PATH``]"""
    ctest_exe: Path | str = attrs.field(default=None, converter=_convert_ctest_exe)
    """CTest executable to use [default search from ``PATH``]"""

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
