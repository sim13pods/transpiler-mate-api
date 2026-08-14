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

"""Stable contracts for independently packaged transpiler-mate plugins."""

from transpiler_mate.api.plugin import (
    EmptyOptions,
    PluginError,
    PluginExecutionError,
    PluginFailureError,
    PluginRegistration,
    TranspilerContext,
    TranspilerContextResolver,
    TranspilerPlugin,
    transpiler_plugin,
)
from transpiler_mate.api.software_application_models import (
    AuthorRole,
    ContributorRole,
    CreativeWork,
    DefinedTerm,
    ImageObject,
    Model,
    Organization,
    Person,
    Role,
    SoftwareApplication,
    SoftwareApplicationModel,
    SoftwareSourceCode,
)

__all__ = [
    "AuthorRole",
    "ContributorRole",
    "CreativeWork",
    "DefinedTerm",
    "EmptyOptions",
    "ImageObject",
    "Model",
    "Organization",
    "Person",
    "PluginError",
    "PluginExecutionError",
    "PluginFailureError",
    "PluginRegistration",
    "Role",
    "SoftwareApplication",
    "SoftwareApplicationModel",
    "SoftwareSourceCode",
    "TranspilerContext",
    "TranspilerContextResolver",
    "TranspilerPlugin",
    "transpiler_plugin",
]
