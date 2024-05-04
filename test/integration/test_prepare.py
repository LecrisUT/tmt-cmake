from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytest_check.context_manager import CheckContextManager

DATA_DIR = (Path(__file__).parent / "data" / "prepare").resolve()


def test_default(
    check: CheckContextManager,
    tmt_cli,
) -> None:
    """
    TODO: Mock the cli calls. Blocked by:
    https://github.com/flexmock/flexmock/pull/162

    .. code-block:: python

        configure_cmd = flexmock(Command)
        configure_cmd.should_receive("run").once()
        build_cmd = flexmock(Command)
        build_cmd.should_receive("run").once()
        mock_command = flexmock(Command)
        (
            mock_command.should_receive("__new__")
            .with_args("cmake", str, str)
            .and_return(configure_cmd)
            .once()
        )
        (
            mock_command.should_receive("__new__")
            .with_args("cmake", str, str)
            .and_return(build_cmd)
            .once()
        )
    """
    args = [
        f"--root={DATA_DIR}",
        "run",
        "-ravvv",
        # TODO: parametrize the `provision.how`
        # Currently cannot use other provision because of missing mock support
        # for `Command`
        "provision",
        "--how=local",
        "plan",
        "--name=default",
    ]
    result = tmt_cli(args)
    check.equal(result.exit_code, 0)
    check.is_true(re.search(r"cmd: cmake -S.* -B.*", result.stdout))
    check.is_in("out: -- Configuring done", result.stdout)
    check.is_in("out: -- Generating done", result.stdout)
    check.is_true(
        re.search(r"out: -- Build files have been written to: .*", result.stdout),
    )
    check.is_true(re.search(r"cmd: cmake --build .*", result.stdout))
    check.is_in("out: dummy_target", result.stdout)
    check.is_in("out: Built target dummy", result.stdout)
