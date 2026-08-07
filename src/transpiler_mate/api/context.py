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

"""Canonical plugin execution context passed to one selected plugin."""

from __future__ import annotations

from pathlib import Path

from cwl_utils.parser import Process
from pydantic import AnyUrl, BaseModel, ConfigDict

from transpiler_mate.api.software_application_models import SoftwareApplication


class TranspilerContext(BaseModel):
    """Resolved CWL input and normalized metadata prepared by a runtime."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
        frozen=True,
    )

    source: Path | AnyUrl
    document: Process | tuple[Process, ...]
    metadata: SoftwareApplication

    @property
    def processes(self) -> tuple[Process, ...]:
        """Return an immutable iterable view while preserving `document`."""

        if isinstance(self.document, tuple):
            return self.document
        return (self.document,)


# TranspilerContext.model_rebuild()
