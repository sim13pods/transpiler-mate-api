# Failure semantics

The exception split answers one question for a runtime: did the requested transformation fail because the domain request is unsupported, or because execution machinery broke?

## Failure versus execution error

`PluginFailureError` is a negative domain result. The plugin recognized the request, applied its rules, and determined that it cannot produce the target. The same input and options should normally fail again until the user changes them or the plugin gains support.

`PluginExecutionError` means the plugin intended to support the request but could not complete it. The cause may be transient, such as an unavailable service, or persistent, such as a bug or broken installation. The type alone does not promise that retrying is safe.

This distinction is about semantics, not blame. A missing user-selected file may be a domain failure, while a missing template shipped inside the plugin is an execution error, even though both can originate as `FileNotFoundError`.

## What the types do not decide

Neither class carries a retry flag, error code, details dictionary, or affected artifacts. The API also does not map the types to terminal exit codes, HTTP statuses, logs, or user-interface severity.

A runtime may use the distinction as one input to those decisions, but must define its own policy. In particular, it should not blindly retry `PluginExecutionError`: `execute` has side effects and the API makes no idempotency or transaction guarantee.

## Why causal chaining matters

Wrapping a low-level exception provides stable public semantics and a useful plugin-level message. Python's `raise NewError(...) from error` preserves the original error as `__cause__`, allowing diagnostic tooling to retain the exact technical reason.

An existing `PluginError` has already crossed that classification boundary. Rewrapping it can accidentally turn a domain refusal into a technical fault, so it should normally be re-raised unchanged.

## Validation is a separate phase

Pydantic `ValidationError` generally means a host could not construct `options_model` or `TranspilerContext`. Plugin execution has not yet produced either domain result. Once execution begins, document-specific compatibility checks belong to the plugin and should use `PluginFailureError`; failures of generation machinery should use `PluginExecutionError`.
