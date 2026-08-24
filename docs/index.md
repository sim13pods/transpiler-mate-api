# Transpiler Mate API

`transpiler-mate-api` is the stable, execution-environment-neutral contract shared by Transpiler Mate runtimes and independently distributed transpiler plugins.

Use it to declare a stateless plugin, describe its typed options, inspect a runtime-prepared CWL context, and report failures in a form a host can understand.

## Choose what you need

- **Learn by building:** [Build your first plugin](tutorials/build-your-first-plugin.md) starts with an empty package and finishes with a tested plugin.
- **Complete a task:** the [how-to guides](how-to/develop-a-plugin.md) cover packaging, options, nested source resolution, errors, and tests.
- **Look up a contract:** the [plugin API](reference/plugin-api.md), [context API](reference/context-api.md), and [exception contract](reference/exceptions.md) describe the public surface precisely.
- **Understand the design:** [Architecture and boundaries](explanation/architecture.md) explains what belongs to this API, a plugin, and a runtime.

## Scope

This package provides Python contracts. It deliberately does **not** provide:

- plugin discovery or a Python entry-point group;
- a command-line or HTTP interface;
- CWL source loading and normalization;
- application orchestration;
- an output or artifact protocol;
- logging, retry, exit-code, or error-rendering policy.

Those responsibilities belong to a runtime. Consequently, a plugin package can expose a valid plugin object using this API, but the host runtime determines how that object is discovered and invoked.

## Requirements

- Python 3.10 or newer
- Pydantic 2
- CWL objects from `cwl-utils`

Install the public contract with:

```bash
python -m pip install transpiler-mate-api
```
