# Context API

## `TranspilerContext`

An immutable Pydantic model prepared by a runtime and passed to plugin execution.

| Field | Type | Meaning |
| --- | --- | --- |
| `source` | `pydantic.AnyUrl` | Canonical source URL. A local path is represented as a `file://` URL. |
| `metadata` | `SoftwareApplication` | Normalized Schema.org-style metadata for the software application. |
| `document` | `Process \| tuple[Process, ...]` | Parsed CWL document, preserving whether one or multiple processes were loaded. |
| `resolved_process` | `Process \| None` | Specifically selected process, or `None` when no individual process was selected. |
| `resolver` | `TranspilerContextResolver` | Runtime-provided service for resolving another location. |

Configuration is `arbitrary_types_allowed=True`, `extra="forbid"`, and `frozen=True`. Consequently, callers cannot add undeclared data or mutate fields after construction.

### `processes`

```python
@property
def processes(self) -> tuple[Process, ...]: ...
```

Returns `document` unchanged when it is already a tuple; otherwise wraps its single process in a one-element tuple. Use this when logic treats single- and multi-process documents uniformly. Use `document` when the distinction itself matters.

## `TranspilerContextResolver`

A runtime-checkable protocol:

```python
def resolve(self, location: str) -> TranspilerContext: ...
```

It resolves a string location to another complete context. The protocol does not define accepted schemes, relative-reference behavior, caching, authentication, network policy, or its exception surface; those are runtime responsibilities.

## Important distinctions

- `source` identifies the loaded source; it is not necessarily a filesystem path.
- `document` is what was loaded; `resolved_process` is the particular process selected for work.
- `resolved_process=None` is valid and commonly means that the whole document is the target.
- `resolver` is a host service, not a guarantee that every URL scheme is available.
