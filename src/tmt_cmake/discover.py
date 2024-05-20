"""
Discover tmt plugin.

This module provides the `discover.how=cmake` plugin.
"""

from __future__ import annotations

import dataclasses
import json
from typing import TYPE_CHECKING

import tmt
import tmt.utils
from tmt.steps.discover import DiscoverPlugin, DiscoverStepData
from tmt.utils import field

import tmt_cmake.prepare

from .cmake import CMake, CTestTest

if TYPE_CHECKING:
    from tmt.steps import Step
    from tmt.steps.provision import Guest
    from tmt.utils import Environment, Path

    from .prepare import PrepareCMake, PrepareCMakeData

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
    test_prefix: str = field(
        option="--prefix",
        default="/ctest",
        help="Test prefix to prepend to ctest test names",
    )
    run_ctest_once: bool = field(
        option="--run-ctest-once",
        default=True,
        is_flag=True,
        help="Run all ctest tests together",
    )
    ctest_exe: Path | None = field(
        option="--ctest-exe",
        default=None,
        metavar="PATH",
        help="Path to CTest executable. [Default: ctest in PATH]",
        show_default=False,
    )


@tmt.steps.provides_method("cmake")
class DiscoverCMake(DiscoverPlugin[DiscoverCMakeData]):
    """
    Find all ctest tests.

    Must contain a prepare CMake step.
    """

    _data_class = DiscoverCMakeData
    prepare: PrepareCMake | None = None
    _tests: list[tmt.Test]
    _cmake: CMake | None = None

    def __init__(  # noqa: D107
        self,
        *,
        step: Step,
        data: DiscoverCMakeData,
        workdir: tmt.utils.WorkdirArgumentType = None,
        logger: tmt.log.Logger,
    ) -> None:
        super().__init__(step=step, data=data, workdir=workdir, logger=logger)
        self._tests = []

    def _check(self) -> bool:
        """Check that the discover step is well configured."""
        successful = True
        # Check that there is a prepare CMake step
        if not self._get_prepare_data():
            self.fail("No CMake prepare step found")
            successful = False
        return successful

    def _get_prepare_data(self) -> PrepareCMakeData | None:
        """Get the corresponding CMake prepare data."""
        # If the prepare was already registered, use that
        if self.prepare:
            return self.prepare.data
        # TODO: tmt does not have a cleaner way to check the plugin type
        cmake_data = [
            data
            for data in self.step.plan.prepare.data
            if isinstance(data, tmt_cmake.prepare.PrepareCMakeData)
        ]
        # Return None as invalid if there is no CMake prepare data
        if not cmake_data:
            return None
        # Otherwise get the actual data
        # If there is more than 1 CMake prepare, this is caught by the prepare step
        return cmake_data[0]

    @property
    def cmake(self) -> CMake:
        """Cached CMake wrapper."""
        if self._cmake is None:
            prepare_data = self._get_prepare_data()
            assert prepare_data is not None
            self._cmake = CMake.from_prepare_data(
                prepare_data,
                self,
                ctest_exe=self.data.ctest_exe,
            )
        return self._cmake

    def _filter_args(self) -> list[str]:
        """Construct the filter arguments from discovery data."""
        args = []
        if self.data.tests_include:
            args += ["-R", self.data.tests_include]
        if self.data.tests_exclude:
            args += ["-E", self.data.tests_exclude]
        if self.data.labels_include:
            args += ["-L", self.data.labels_include]
        if self.data.labels_exclude:
            args += ["-LE", self.data.labels_exclude]
        return args

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
        if phase_name is not None and phase_name != self.name:
            return []

        if enabled is None:
            return self._tests

        return [test for test in self._tests if test.enabled is enabled]

    def do_discover(
        self,
        guest: Guest,
        environment: Environment | None,
    ) -> None:
        """Do the actual discover."""
        output = guest.execute(
            self.cmake.test("--show-only=json-v1", *self._filter_args()),
            env=environment,
        )
        assert output.stdout
        ctest_json = json.loads(output.stdout)
        for ctest_test in ctest_json["tests"]:
            name = ctest_test["name"]
            tmt_test = CTestTest.from_dict(
                name=f"{self.data.test_prefix}/{name}",
                mapping={
                    "framework": "cmake",
                    # dummy test value will be populated by framework's get_test_command
                    "test": "",
                    "ctest_args": ["-R", rf"^{name}$"],
                },
                logger=self._logger.descend(name),
                discover=self,
            )
            # Update the tests. Currently using the hack in DiscoverFmf.post_dist_git
            self.step.plan.discover._tests[self.name].append(tmt_test)  # noqa: SLF001
            tmt_test.serial_number = self.step.plan.draw_test_serial_number(tmt_test)
        self.step.save()
        self.step.summary()

    def register_single_test(self) -> None:
        """Register single tmt test."""
        name = self.data.test_prefix
        tmt_test_data = {
            "framework": "cmake",
            # dummy test value will be populated by framework's get_test_command
            "test": "",
            "ctest_args": self._filter_args(),
        }
        tmt_test = CTestTest.from_dict(
            name=name,
            mapping=tmt_test_data,
            logger=self._logger.descend(name),
            discover=self,
        )
        self._tests.append(tmt_test)

    def go(self) -> None:  # noqa: D102
        super().go()
        # Save the prepare step for easier referencing
        prepare_plugins = self.step.plan.prepare.phases(tmt_cmake.prepare.PrepareCMake)
        assert len(prepare_plugins) == 1
        self.prepare = prepare_plugins[0]
        # Get the tests
        if self.data.run_ctest_once:
            # If we run all tests together register a single tmt test
            self.register_single_test()
            return
        # Otherwise, tests will be created after prepare step
        self.step.plan.discover.extract_tests_later = True
        self.info("Tests will be discovered after prepare.cmake step is done")
        self.prepare.discover = self
