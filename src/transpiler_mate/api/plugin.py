# Copyright 2026 Terradue
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Framework-independent plugin contracts."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Generic, Protocol, TypeVar, runtime_checkable

from cwl_utils.parser import Process
from pydantic import AnyUrl, BaseModel, ConfigDict

from transpiler_mate.api.software_application_models import SoftwareApplication

OptionsT = TypeVar("OptionsT", bound=BaseModel)


class PluginError(Exception):
    """Base class for errors intentionally exposed by a transpiler plugin."""


class PluginExecutionError(PluginError):
    """Unexpected technical error that prevents a plugin from completing."""


class PluginFailureError(PluginError):
    """Expected domain failure reported by an otherwise working plugin."""


@runtime_checkable
class TranspilerContextResolver(Protocol):
    """Resolves a source into an execution context."""

    def resolve(self, location: str) -> TranspilerContext: ...


class TranspilerContext(BaseModel):
    """Resolved CWL input and normalized metadata prepared by a runtime."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
        frozen=True,
    )

    source: Path | AnyUrl
    metadata: SoftwareApplication
    document: Process | tuple[Process, ...]

    resolver: TranspilerContextResolver

    @property
    def processes(self) -> tuple[Process, ...]:
        """Return an immutable iterable view while preserving `document`."""

        if isinstance(self.document, tuple):
            return self.document
        return (self.document,)


class EmptyOptions(BaseModel):
    """Configuration model for a plugin with no parameters."""

    model_config = ConfigDict(extra="forbid")


class PluginRegistration(BaseModel, Generic[OptionsT]):
    """Immutable metadata and execution function for a stateless plugin."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
        frozen=True,
    )

    name: str
    description: str
    options_model: type[OptionsT]
    execute: Callable[[TranspilerContext, OptionsT], None]


def transpiler_plugin(
    *,
    name: str,
    description: str,
    options_model: type[OptionsT],
) -> Callable[
    [Callable[[TranspilerContext, OptionsT], None]],
    PluginRegistration[OptionsT],
]:
    """Register a stateless plugin from its typed execution function."""

    def register(
        execute: Callable[[TranspilerContext, OptionsT], None],
    ) -> PluginRegistration[OptionsT]:
        return PluginRegistration(
            name=name,
            description=description,
            options_model=options_model,
            execute=execute,
        )

    return register


@runtime_checkable
class TranspilerPlugin(Protocol[OptionsT]):
    """Public contract implemented by one independently packaged plugin."""

    @property
    def name(self) -> str: ...

    @property
    def description(self) -> str: ...

    @property
    def options_model(self) -> type[OptionsT]: ...

    def execute(
        self,
        context: TranspilerContext,
        options: OptionsT,
    ) -> None:
        """Execute without assumptions about CLI, HTTP, workers, or notebooks."""
        ...
