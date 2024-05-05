from __future__ import annotations

from typing import TYPE_CHECKING

import click.testing
import pytest
import tmt.cli
from tmt.base import Core, Plan, Run, Story, Test, Tree
from tmt.utils import Common, MultiInvokableCommon

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from typing import IO, Any

    import click.core  # noqa: TCH004 (false-positive)


def pytest_collection_modifyitems(
    session: pytest.Session,  # noqa: ARG001
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    set_test_type_marker(config, items, "smoke")
    set_test_type_marker(config, items, "unit")
    set_test_type_marker(config, items, "integration")
    set_test_type_marker(config, items, "functional")


def set_test_type_marker(
    config: pytest.Config,
    items: list[pytest.Item],
    test_type: str,
) -> None:
    rootdir = config.rootpath
    test_path = rootdir / "test" / test_type
    for item in items:
        if not item.path.is_relative_to(test_path):
            continue
        item.add_marker(test_type)


class CliRunner(click.testing.CliRunner):
    """
    See tmt's repo `tests` package
    """

    def __call__(  # noqa: PLR0913
        self,
        args: str | Sequence[str] | None = None,
        *,
        input: str | bytes | IO[Any] | None = None,  # noqa: A002
        env: Mapping[str, str | None] | None = None,
        catch_exceptions: bool = True,
        color: bool = False,
        **kwargs: Any,
    ) -> click.testing.Result:
        """Wrapper for :py:meth:`invoke` using :py:func:`tmt.cli.main`"""
        return self.invoke(
            tmt.cli.main,
            args=args,
            input=input,
            env=env,
            catch_exceptions=catch_exceptions,
            color=color,
            **kwargs,
        )

    def invoke(  # noqa: PLR0913
        self,
        cli: click.core.BaseCommand,
        args: str | Sequence[str] | None = None,
        input: str | bytes | IO[Any] | None = None,  # noqa: A002
        env: Mapping[str, str | None] | None = None,
        catch_exceptions: bool = True,  # noqa: FBT001, FBT002
        color: bool = False,  # noqa: FBT001, FBT002
        **extra: Any,
    ) -> click.testing.Result:
        for klass in (Core, Run, Tree, Test, Plan, Story, Common, MultiInvokableCommon):
            klass.cli_invocation = None

        return super().invoke(
            cli,
            args=args,
            input=input,
            env=env,
            catch_exceptions=catch_exceptions,
            color=color,
            **extra,
        )


@pytest.fixture()
def tmt_cli():
    return CliRunner()
