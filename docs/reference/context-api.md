# Context API

## `TranspilerContext`

An immutable Pydantic model prepared by a runtime and passed to plugin execution.

| Field | Type | Meaning |
| --- | --- | --- |
| `source` | `pydantic.AnyUrl` | Canonical source URL. A local path is represented as a `file://` URL. |
| `process_id` | `str \| None` | Optional process fragment identifier selected from the source. Defaults to `None`. |
| `metadata` | `SoftwareApplication` | Normalized Schema.org-style metadata for the software application. |
| `document` | `Mapping[str, Process]` | Parsed CWL processes keyed by process ID. |
| `resolver` | `TranspilerContextResolver` | Runtime-provided service for resolving another location. |

Configuration is `arbitrary_types_allowed=True`, `extra="forbid"`, and
`frozen=True`. Consequently, callers cannot add undeclared data or reassign
fields after construction. This is a shallow freeze: the contract accepts any
`Mapping`, so a mutable mapping supplied by the runtime is not made immutable.

### `processes`

```python
@property
def processes(self) -> Iterable[Process]: ...
```

Returns `document.values()`, so iteration follows the mapping's order. Use
`document` when process IDs or keyed lookup matter.

### `resolved_process`

```python
@property
def resolved_process(self) -> Process: ...
```

Looks up `process_id` in `document`. It raises `PluginExecutionError` when
`process_id` is missing or when it does not name an entry in `document`. It
never returns `None`.

## `TranspilerContextResolver`

A runtime-checkable protocol:

```python
def resolve(self, location: str) -> TranspilerContext: ...
```

It resolves a string location to another complete context. The protocol does not define accepted schemes, relative-reference behavior, caching, authentication, network policy, or its exception surface; those are runtime responsibilities.

## Important distinctions

- `source` identifies the loaded source; it is not necessarily a filesystem path.
- `document` contains every declared process; `process_id` identifies the
  particular process selected for work.
- An unset `process_id` is valid context state, but reading `resolved_process`
  in that state raises `PluginExecutionError`. Plugins that support a whole
  document should use `document` or `processes` instead.
- `resolver` is a host service, not a guarantee that every URL scheme is available.
