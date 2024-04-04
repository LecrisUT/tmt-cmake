"""CMake commands and utilities."""

from __future__ import annotations

import attrs
from tmt.utils import Command, Path


def _convert_cmake_exe(val: Path | None) -> Path | str:
    # No converter decorator yet
    # https://github.com/python-attrs/attrs/pull/404
    return val if val else "cmake"


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

    def configure(
        self,
        preset: str | None = None,
        install_prefix: Path | None = None,
    ) -> Command:
        """
        CMake configure command.

        :param preset: Project's preset to configure
        :param install_prefix: Install prefix
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
