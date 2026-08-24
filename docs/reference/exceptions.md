# Exception contract

The public hierarchy is:

```text
Exception
└── PluginError
    ├── PluginFailureError
    └── PluginExecutionError
```

The classes carry no structured fields beyond normal `Exception` arguments. Their class is the machine-readable category; their message is human-readable context.

## Decision table

| Circumstance | Raise or allow | Reason |
| --- | --- | --- |
| Supported input completes | Return normally | `execute` returns `None`. |
| Valid CWL uses a feature the plugin does not support | `PluginFailureError` | Expected domain rejection. |
| Valid options conflict with this document | `PluginFailureError` | The request cannot be fulfilled, but the plugin is working. |
| Required domain metadata is absent or unsuitable | `PluginFailureError` | Deterministic input/domain problem. |
| Destination exists and `overwrite=False` | `PluginFailureError` | Expected policy refusal. |
| User-supplied template/configuration is well-formed but incompatible | `PluginFailureError` | Expected domain incompatibility. |
| Options fail Pydantic type/field/range validation before execution | Allow `pydantic.ValidationError` | Options could not be constructed; execution did not begin. |
| Programmer calls `execute` with the wrong Python object type | Do not translate automatically | This violates the typed calling contract. |
| Output cannot be written because of an I/O or permission error | `PluginExecutionError` from the original error | Technical machinery prevented completion. |
| Required executable cannot start or exits unexpectedly | `PluginExecutionError` | Technical dependency failed. |
| Remote service is unavailable, times out, or returns a malformed response | `PluginExecutionError` | Infrastructure/dependency failure. |
| Serializer, template engine, or target SDK crashes | `PluginExecutionError` from the original error | Supported execution malfunctioned. |
| An internal invariant is violated | `PluginExecutionError` | Plugin defect or unexpected state. |
| Called helper already raises `PluginFailureError` or `PluginExecutionError` | Re-raise unchanged | Preserve its classification and traceback. |
| A custom, intentionally public plugin condition needs its own stable category | Subclass `PluginError` only when host coordination exists | Hosts can still catch the common base. |
| Cancellation, `KeyboardInterrupt`, `SystemExit`, or `GeneratorExit` | Do not catch | These inherit from `BaseException`, not ordinary operational `Exception`. |

## Ambiguous I/O cases

Classify by meaning, not by the originating built-in exception alone:

- A user asks not to overwrite an existing destination: `PluginFailureError`.
- The plugin accepted the destination but the filesystem fails during a write: `PluginExecutionError`.
- A required, user-selected domain input file does not exist: usually `PluginFailureError` because the request is not satisfiable.
- A plugin-owned installed resource is missing: `PluginExecutionError` because the installation or plugin is broken.

## `PluginError`

The common base for failures intentionally exposed by a plugin. Hosts may catch it to distinguish classified plugin errors from arbitrary exceptions.

Normally raise one of the two specific subclasses. Raising `PluginError` directly discards the failure-versus-execution distinction.

## `PluginFailureError`

An expected domain failure reported by an otherwise working plugin. “Expected” means the plugin deliberately recognizes and rejects the circumstance, not that success was expected.

The class does not imply an exit status, HTTP status, retry policy, or log level. A host decides those mappings.

## `PluginExecutionError`

An unexpected technical error that prevents completion. Wrap lower-level errors with causal chaining:

```python
try:
    render()
except TemplateEngineError as error:
    raise PluginExecutionError("could not render target files") from error
```

Do not expose secrets in the added message. Causal chaining retains diagnostic detail for a host or log while keeping the top-level message useful.

## Boundaries not specified here

The API does not prescribe whether a runtime catches unclassified exceptions, retries an execution error, prints a traceback, assigns process exit codes, or serializes an error over HTTP. Plugin authors should classify known public failures consistently; runtime authors define presentation and recovery policy.
