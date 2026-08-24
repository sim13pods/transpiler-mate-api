# Test a plugin

Test the API contract directly. You do not need a CLI, plugin manager, or source loader to exercise `execute`.

## Test registration

```python
from transpiler_mate.api import TranspilerPlugin


def test_registration() -> None:
    assert isinstance(plugin, TranspilerPlugin)
    assert plugin.name == "my-target"
    assert plugin.options_model is Options
```

`TranspilerPlugin` is runtime-checkable, but runtime protocol checks only establish structural presence. Keep a strict type checker in the development suite to verify generic option types and call signatures.

## Build a focused context

```python
from pathlib import Path

from cwl_utils.parser.cwl_v1_2 import Workflow
from pydantic import AnyUrl
from transpiler_mate.api import TranspilerContext
from transpiler_mate.api.software_application_models import SoftwareApplication


class ResolverStub:
    def resolve(self, location: str) -> TranspilerContext:
        raise AssertionError(f"unexpected resolution of {location!r}")


def make_context(tmp_path: Path) -> TranspilerContext:
    return TranspilerContext(
        source=AnyUrl((tmp_path / "workflow.cwl").as_uri()),
        metadata=SoftwareApplication.model_construct(),
        document=Workflow(inputs=[], outputs=[], steps=[]),
        resolver=ResolverStub(),
    )
```

Use `model_construct()` only when bypassing unrelated validation is intentional. Construct complete validated metadata when the behavior under test reads it.

## Test both failure categories

```python
import pytest
from transpiler_mate.api import PluginExecutionError, PluginFailureError


def test_rejects_an_unsupported_construct(context, options) -> None:
    with pytest.raises(PluginFailureError, match="scatter"):
        plugin.execute(context, options)


def test_reports_generator_crash(context, options, monkeypatch) -> None:
    monkeypatch.setattr(target_sdk, "generate", crash)

    with pytest.raises(PluginExecutionError) as raised:
        plugin.execute(context, options)

    assert raised.value.__cause__ is not None
```

Also assert observable side effects: exact file content, encoding, directory layout, and whether partial output remains after failure. If the plugin calls `context.resolver`, use a recording stub and assert the location passed to it.

## Run repository checks

For this API repository itself, the configured test command is:

```bash
hatch run test:test
```

Plugin projects may use any test environment, but should test against every Python and API version range they claim to support.
