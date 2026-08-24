# Resolve another CWL source

The runtime places a `TranspilerContextResolver` in every context. Use it when a plugin must load another CWL location using the same normalization policy as the host.

```python
from transpiler_mate.api import (
    PluginError,
    PluginExecutionError,
    TranspilerContext,
)


def load_library(context: TranspilerContext, location: str) -> TranspilerContext:
    try:
        return context.resolver.resolve(location)
    except PluginError:
        raise
    except Exception as error:
        raise PluginExecutionError(
            f"could not resolve supporting CWL source {location!r}"
        ) from error
```

Pass a location string accepted by the runtime. Although `TranspilerContext.source` is always an `AnyUrl`, the resolver protocol deliberately accepts `str` so a runtime can define its own location syntax and relative-resolution behavior.

Do not instantiate a context resolver or reload `context.source` just to access the current document. The runtime has already prepared:

- `context.document`, preserving one `Process` versus a tuple of processes;
- `context.processes`, a uniform tuple view;
- `context.resolved_process`, the selected process when one was selected;
- `context.metadata`, normalized `SoftwareApplication` metadata.

The resolver may raise exceptions defined by its runtime. Preserve an existing `PluginError`; wrap an unexpected lower-level exception only at a boundary where your plugin can add useful operation and location context. Ask the target runtime whether it already normalizes resolver failures before adding a wrapper.
