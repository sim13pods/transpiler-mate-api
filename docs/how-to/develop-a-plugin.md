# Develop and package a plugin

Use this guide as a production checklist for a custom plugin.

## Declare the dependency

Give the plugin its own distribution and depend on the API package rather than on a particular CLI or server:

```toml
[project]
name = "transpiler-mate-my-target"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = ["transpiler-mate-api>=1,<2"]
```

Pin a major-version range you test. Add target SDKs, template engines, or serializers as your plugin's own dependencies.

## Choose an options model

For a configurable plugin, create a Pydantic model:

```python
from pathlib import Path

from pydantic import BaseModel, ConfigDict


class Options(BaseModel):
    model_config = ConfigDict(extra="forbid")

    output_directory: Path
    overwrite: bool = False
```

For a plugin with no parameters, use the provided `EmptyOptions`. It also rejects unexpected fields.

## Implement a stateless function

```python
from transpiler_mate.api import TranspilerContext, transpiler_plugin


@transpiler_plugin(
    name="my-target",
    description="Generate files for My Target",
    options_model=Options,
)
def plugin(context: TranspilerContext, options: Options) -> None:
    for process in context.processes:
        generate(process, options.output_directory, options.overwrite)
```

Keep run-specific mutable state local to `execute`. A runtime may retain and reuse the registration object; the public contract makes no single-use or concurrency guarantee.

The execution signature is exact in intent:

```python
def execute(context: TranspilerContext, options: OptionsT) -> None: ...
```

- Read the parsed CWL processes from the ID-to-process mapping in
  `context.document`, or iterate over `context.processes` when the IDs are not
  needed.
- Use `context.get_processes_by_type(ProcessType)` when the plugin accepts only
  a particular CWL process type. Top-level union aliases such as
  `cwl_utils.parser.Workflow` select that type across supported CWL versions.
  Supply `process_ids` to restrict the lookup, or set `fail_if_empty=False`
  when no match is a valid outcome.
- Use `context.resolved_process` when the plugin requires the process selected
  by `context.process_id`. Access raises `PluginExecutionError` if the source
  did not select a process or if the selected ID is absent from `document`.
- Read normalized software metadata from `context.metadata`.
- Use `context.resolver` when you deliberately need another source.
- Produce results through side effects. The contract does not define a returned artifact list.

## Export the registration

```python
# src/my_target/__init__.py
from my_target.plugin import plugin

__all__ = ["plugin"]
```

The decorated value is a `PluginRegistration` and structurally implements `TranspilerPlugin`. A host can import it and inspect `name`, `description`, `options_model`, and `execute`.

## Integrate with a runtime

Stop at the runtime boundary and consult that runtime's documentation. This repository does not specify:

- a package naming scheme;
- an entry-point group;
- a module-level variable name;
- plugin uniqueness rules;
- CLI option conversion;
- activation, ordering, or discovery.

If a runtime asks for a `TranspilerPlugin`, pass the exported registration. If it asks for an entry point or adapter, configure exactly the group or wrapper that runtime documents.

## Make writes robust

Validate the complete domain input before producing files where practical. For multi-file output, write to a staging directory and publish only after generation succeeds. If execution fails, remove only temporary artifacts the current invocation owns; never broadly delete an output directory.

Return normally on success. Use the exception policy in [Report failures correctly](report-failures.md) for failures.

## Verify the contract

At minimum, test:

- registration metadata and `options_model`;
- valid and invalid options;
- single-entry and multi-entry process mappings;
- successful `resolved_process` selection and the missing/unknown
  `process_id` errors, if the plugin uses that property;
- every supported domain rejection as `PluginFailureError`;
- technical dependency failures as `PluginExecutionError`;
- the exception message and preserved cause;
- absence or cleanup of partial output.

See [Test a plugin](test-a-plugin.md) for patterns.
