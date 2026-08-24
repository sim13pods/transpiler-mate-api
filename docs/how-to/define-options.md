# Define and validate options

Set `options_model` to a Pydantic `BaseModel` subclass. This keeps the transport representation—CLI strings, JSON, or worker messages—outside the plugin's execution logic.

## Reject misspelled fields

```python
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Options(BaseModel):
    model_config = ConfigDict(extra="forbid")

    output: Path
    dialect: Literal["stable", "experimental"] = "stable"
    workers: int = Field(default=1, ge=1)
```

Use Pydantic validators for shape, type, range, and relationships that can be checked without the resolved document. A host normally constructs this model before calling `execute`.

## Use no options

```python
from transpiler_mate.api import EmptyOptions, TranspilerContext, transpiler_plugin


@transpiler_plugin(
    name="fixed-target",
    description="Generate the fixed target format",
    options_model=EmptyOptions,
)
def plugin(context: TranspilerContext, options: EmptyOptions) -> None:
    ...
```

`EmptyOptions` is not an invitation to accept arbitrary configuration: its `extra="forbid"` setting rejects every unknown field.

## Separate option validation from domain validation

- Invalid types, missing option fields, forbidden extra fields, and numeric constraints should produce Pydantic `ValidationError` while constructing the options model.
- A well-formed option that cannot be honored for this particular CWL document should cause `PluginFailureError` during execution.
- A valid option that fails because an external tool crashes should cause `PluginExecutionError` during execution.

For example, validate that `workers >= 1` in the model. If `dialect="stable"` is valid in general but the current document uses an experimental CWL feature, raise `PluginFailureError` from `execute`.

Do not catch a `ValidationError` merely to relabel it as a plugin error unless the validation occurs inside execution and you can add meaningful domain context. Runtime behavior for top-level option validation is outside this API.
