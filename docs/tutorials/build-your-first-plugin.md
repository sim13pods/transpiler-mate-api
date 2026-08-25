# Build your first plugin

This tutorial creates a small plugin that writes the names and CWL classes found in a resolved document to JSON. Along the way, you will define options, register the execution function, report a domain failure, and test the result without a runtime.

## 1. Create the package

Start with this layout:

```text
process-inventory/
├── pyproject.toml
├── src/
│   └── process_inventory/
│       ├── __init__.py
│       └── plugin.py
└── tests/
    └── test_plugin.py
```

Create `pyproject.toml`:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "transpiler-mate-process-inventory"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
  "transpiler-mate-api>=1,<2",
]

[project.optional-dependencies]
test = ["pytest>=8"]
```

The dependency range is an example for the current API major version. Adjust it to the compatibility range your plugin actually tests.

!!! important
    This API package defines no discovery entry-point group. Do not copy an invented `[project.entry-points]` section. Export the plugin object from your package and follow the chosen runtime's discovery documentation.

## 2. Define typed options

Create `src/process_inventory/plugin.py`:

```python
from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from transpiler_mate.api import (
    PluginFailureError,
    TranspilerContext,
    transpiler_plugin,
)


class InventoryOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    output: Path
    indent: int = Field(default=2, ge=0, le=8)
```

`options_model` must be a `BaseModel` subclass. Pydantic supplies coercion and validation before execution when a host constructs it. `extra="forbid"` catches misspelled option names instead of silently ignoring them.

## 3. Register the execution function

Continue in the same file:

```python
@transpiler_plugin(
    name="process-inventory",
    description="Write an inventory of the resolved CWL processes",
    options_model=InventoryOptions,
)
def plugin(context: TranspilerContext, options: InventoryOptions) -> None:
    rows = [
        {
            "id": getattr(process, "id", None),
            "class": type(process).__name__,
        }
        for process in context.processes
    ]

    if not rows:
        raise PluginFailureError("the CWL document contains no processes")

    options.output.write_text(
        json.dumps(rows, indent=options.indent) + "\n",
        encoding="utf-8",
    )
```

The decorator replaces the function name with an immutable `PluginRegistration`. The original function is available as `plugin.execute`. Execution returns `None`; files and other results are side effects owned by the plugin.

`context.document` maps process IDs to parsed CWL `Process` objects. The
`context.processes` iterable exposes its values when a plugin does not need the
IDs.

## 4. Export the plugin object

Create `src/process_inventory/__init__.py`:

```python
from process_inventory.plugin import plugin

__all__ = ["plugin"]
```

This makes the object importable as `process_inventory.plugin`. Importability is not the same as runtime discovery: wire this object into the target runtime using that runtime's adapter or discovery mechanism.

## 5. Test execution directly

Create `tests/test_plugin.py`:

```python
from pathlib import Path

from cwl_utils.parser.cwl_v1_2 import Workflow
from pydantic import AnyUrl

from process_inventory import plugin
from process_inventory.plugin import InventoryOptions
from transpiler_mate.api import TranspilerContext
from transpiler_mate.api.software_application_models import SoftwareApplication


class UnusedResolver:
    def resolve(self, location: str) -> TranspilerContext:
        raise AssertionError("the plugin should not resolve another source")


def test_writes_an_inventory(tmp_path: Path) -> None:
    output = tmp_path / "inventory.json"
    process = Workflow(id="main", inputs=[], outputs=[], steps=[])
    context = TranspilerContext(
        source=AnyUrl((tmp_path / "workflow.cwl").as_uri()),
        metadata=SoftwareApplication.model_construct(),
        document={"main": process},
        resolver=UnusedResolver(),
    )

    plugin.execute(context, InventoryOptions(output=output))

    assert '"class": "Workflow"' in output.read_text(encoding="utf-8")
```

`SoftwareApplication.model_construct()` keeps this focused test small by bypassing validation of metadata the plugin never reads. Use a fully validated model in tests that depend on metadata.

Run it:

```bash
python -m pip install -e '.[test]'
pytest
```

You now have the API-side portion of a plugin: a packaged, typed, importable, and directly testable `TranspilerPlugin`. The remaining discovery step is deliberately runtime-specific.
