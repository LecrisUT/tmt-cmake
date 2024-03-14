from importlib.metadata import version

import tmt_cmake


def test_version() -> None:
    assert tmt_cmake.__version__ == version("tmt-cmake")
