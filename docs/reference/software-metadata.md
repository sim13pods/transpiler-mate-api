# Software metadata models

`TranspilerContext.metadata` is a `SoftwareApplication`. The public package also exports the generated supporting models:

- `SoftwareApplicationModel`
- `Organization`
- `Person`
- `Role`, `AuthorRole`, and `ContributorRole`
- `DefinedTerm`
- `CreativeWork`
- `ImageObject`
- `SoftwareApplication`
- `SoftwareSourceCode`
- `Model`, a root model containing `SoftwareApplication`

These Pydantic models represent a constrained Schema.org vocabulary generated from `schemas/software_application.yaml`.

## Input aliases

Fields accept the aliases declared by their generated model. For example, `SoftwareApplication.name` accepts `name` and `https://schema.org/name`; `@type` selects the Schema.org type where applicable. Consult each model's Pydantic field metadata for the exact accepted aliases.

## Serialization defaults

`SoftwareApplicationModel.model_dump()` defaults to:

- `mode="json"`, so URLs and dates become JSON-compatible values;
- `exclude_none=True`;
- Schema.org serialization aliases only when the caller explicitly passes `by_alias=True`.

Example:

```python
data = context.metadata.model_dump(by_alias=True)
```

Unknown fields are allowed on these metadata models. This differs deliberately from `PluginRegistration`, `TranspilerContext`, and `EmptyOptions`, which forbid extras.

## Required `SoftwareApplication` fields

The current generated model requires `name`, `description`, `date_created`, `license`, `software_version`, `software_help`, `publisher`, and `author`. Other declared fields are optional. Rely on the Python model and source schema as the authoritative field-level contract.

The generated Python file should not be hand-edited. Update `schemas/software_application.yaml` and regenerate it with the repository's `process_schemaorg` task.
