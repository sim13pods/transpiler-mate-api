# Report failures correctly

Raise the exception that tells the host whether the plugin rejected the requested transformation or malfunctioned while trying to perform it.

## Raise `PluginFailureError` for expected domain rejection

```python
from transpiler_mate.api import PluginFailureError


if not supports(process):
    raise PluginFailureError(
        f"process {process.id!r} uses scatter, which this target does not support"
    )
```

Use it when the plugin is operating correctly and has enough information to give a deterministic, actionable refusal. Typical cases are unsupported CWL constructs, an incompatible option/document combination, a user-selected destination that already exists when overwrite is disabled, or missing domain data required for generation.

## Raise `PluginExecutionError` for technical failure

```python
from transpiler_mate.api import PluginExecutionError


try:
    completed = run_generator(command)
except OSError as error:
    raise PluginExecutionError("could not start the target generator") from error

if completed.returncode != 0:
    raise PluginExecutionError(
        f"target generator exited with status {completed.returncode}"
    )
```

Use it when a supported operation could not complete because machinery failed: a subprocess could not start or crashed, generated output could not be written, a required service became unavailable, or an internal invariant was violated.

## Preserve errors that are already classified

```python
from transpiler_mate.api import PluginError, PluginExecutionError


try:
    generate()
except PluginError:
    raise
except Exception as error:
    raise PluginExecutionError("generation failed") from error
```

Catch narrowly whenever possible. If a boundary catch is necessary, catch `Exception`, not `BaseException`, so cancellation signals such as `KeyboardInterrupt` and `SystemExit` still propagate. Use `raise ... from error` to keep the original traceback.

## Write useful messages

State the failed operation, relevant subject, and a remedy when known:

```text
process 'align': scatter method 'dotproduct' is unsupported; use 'nested_crossproduct'
```

Do not include credentials, access tokens, complete environment dumps, or sensitive source contents. Do not assume whether the host shows the message in a terminal, JSON response, notebook, or worker log.

For a complete circumstance table, see the [exception contract](../reference/exceptions.md).
