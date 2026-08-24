# Architecture and boundaries

The API is a small dependency-inversion boundary. A runtime owns environment-specific work; a plugin owns one transformation; both depend on the same stable contract.

```text
runtime
  loads and normalizes CWL + metadata
  constructs options and TranspilerContext
  discovers plugin by runtime-specific means
                     │
                     ▼
             TranspilerPlugin.execute
                     │
                     ▼
plugin
  validates domain support
  generates target-specific side effects
  returns None or raises PluginError
```

## Why the registration is data

`@transpiler_plugin` turns a function into an immutable `PluginRegistration`. A host can inspect metadata and the options model without constructing a stateful plugin class. The execution function remains independent of Click, HTTP servers, workers, and notebooks.

The `TranspilerPlugin` protocol also permits other implementations. Structural typing avoids forcing inheritance, while `PluginRegistration` provides the convenient standard implementation.

## Why the context is immutable

The runtime prepares a normalized snapshot containing source identity, parsed CWL, selected process, metadata, and a resolver. Freezing that model prevents a plugin from accidentally rewriting shared invocation state. Plugin output belongs in plugin-owned side effects, not mutations to the context.

## Why discovery is absent

Discovery couples packages to deployment policy: entry-point groups, enablement, naming, ordering, and duplicate handling. Keeping it out of this package lets a CLI, web service, notebook, or worker use the same plugin contract with a suitable adapter.

This means “custom plugin” has two layers:

1. Implement and export an object satisfying `TranspilerPlugin` using this package.
2. Connect that object using the chosen runtime's separately documented mechanism.

The first layer is portable. The second is intentionally host-specific.

## Why execution returns `None`

The current contract treats generation as side-effecting work and imposes no universal artifact representation. A plugin might write a directory, call an external generator, update a service, or emit several related files. Artifact discovery, atomic publication, and cleanup policy therefore remain plugin/runtime concerns rather than API return values.
