# Plugin API

Import the public plugin symbols from `transpiler_mate.api`.

## `transpiler_plugin`

```python
transpiler_plugin(
    *,
    name: str,
    description: str,
    options_model: type[OptionsT],
) -> Callable[[Callable[[TranspilerContext, OptionsT], None]], PluginRegistration[OptionsT]]
```

A decorator factory that converts one typed execution function into a `PluginRegistration`.

No normalization or non-empty constraint is imposed on `name` or `description` by the current model. Any naming and uniqueness rules are host policy.

## `PluginRegistration[OptionsT]`

An immutable Pydantic model implementing the plugin shape.

| Field | Type | Meaning |
| --- | --- | --- |
| `name` | `str` | Host-facing plugin name. |
| `description` | `str` | Human-readable purpose. |
| `options_model` | `type[OptionsT]` | Pydantic model class used for configuration. |
| `execute` | `Callable[[TranspilerContext, OptionsT], None]` | Stateless execution function. |

The model allows arbitrary Python types because it stores a class and callable, forbids extra fields, and is frozen. Mutation raises Pydantic `ValidationError`.

## `TranspilerPlugin[OptionsT]`

A `runtime_checkable` structural protocol with read-only `name`, `description`, and `options_model` properties plus:

```python
def execute(self, context: TranspilerContext, options: OptionsT) -> None: ...
```

A custom object can implement this protocol without using the decorator. The decorator is the shortest supported way to produce a conforming, stateless registration.

`isinstance(value, TranspilerPlugin)` is available for a shallow runtime structural check. Use static type checking for precise signature and generic compatibility.

## `EmptyOptions`

A Pydantic model for a plugin with no configuration fields. Unknown fields are forbidden.

```python
EmptyOptions()                         # valid
EmptyOptions.model_validate({"x": 1}) # raises ValidationError
```

## Execution contract

`execute` receives a fully constructed context and an instance of the declared options model. It returns `None`. This API does not define async execution, returned artifacts, progress callbacks, logging, cancellation, or transaction semantics.
