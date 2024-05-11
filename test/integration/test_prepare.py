from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytest_check.context_manager import CheckContextManager
    from pytest_subprocess.fake_process import FakeProcess

DATA_DIR = (Path(__file__).parent / "data" / "prepare").resolve()


def test_default(
    fp: FakeProcess,
    check: CheckContextManager,
    tmt_cli,
) -> None:
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
    fp.register(["cmake", fp.any(min=2)], returncode=1)
    fp.register(["cmake", "--build", fp.any(min=1)], returncode=1)
    fp.allow_unregistered(allow=True)
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
