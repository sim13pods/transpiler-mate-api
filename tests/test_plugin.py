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

from pathlib import Path
from typing import cast

import pytest
from cwl_utils.parser.cwl_v1_2 import Workflow
from pydantic import AnyUrl, BaseModel, ValidationError

import transpiler_mate.api as api
from transpiler_mate.api import (
    PluginError,
    PluginExecutionError,
    PluginFailureError,
    PluginRegistration,
    TranspilerContext,
    TranspilerPlugin,
    transpiler_plugin,
)
from transpiler_mate.api.software_application_models import SoftwareApplication


class Options(BaseModel):
    output: Path


def test_transpiler_plugin_registers_typed_execution_function() -> None:
    executed_with: list[Path] = []

    @transpiler_plugin(
        name="test",
        description="Test registration",
        options_model=Options,
    )
    def plugin(
        context: TranspilerContext,
        options: Options,
    ) -> None:
        executed_with.append(options.output)

    conforms: TranspilerPlugin[Options] = plugin

    assert isinstance(plugin, PluginRegistration)
    assert conforms.name == "test"
    assert plugin.description == "Test registration"
    assert plugin.options_model is Options
    context = cast("TranspilerContext", object())
    assert plugin.execute(context, Options(output=Path("out.txt"))) is None
    assert executed_with == [Path("out.txt")]


def test_plugin_registration_is_an_immutable_pydantic_model() -> None:
    def execute(
        context: TranspilerContext,
        options: Options,
    ) -> None:
        pass

    registration = PluginRegistration(
        name="test", description="Test", options_model=Options, execute=execute
    )

    assert registration.model_dump() == {
        "name": "test",
        "description": "Test",
        "options_model": Options,
        "execute": execute,
    }
    with pytest.raises(ValidationError, match="Instance is frozen"):
        registration.name = "changed"
    assert isinstance(registration, BaseModel)


def test_plugin_exceptions_share_a_common_base() -> None:
    assert issubclass(PluginExecutionError, PluginError)
    assert issubclass(PluginFailureError, PluginError)


def test_software_application_models_are_exported_from_api() -> None:
    expected_models = {
        "AuthorRole",
        "ContributorRole",
        "CreativeWork",
        "DefinedTerm",
        "ImageObject",
        "Model",
        "Organization",
        "Person",
        "Role",
        "SoftwareApplication",
        "SoftwareSourceCode",
    }

    assert expected_models <= set(api.__all__)
    for model_name in expected_models:
        assert getattr(api, model_name).__module__ == (
            "transpiler_mate.api.software_application_models"
        )


def test_transpiler_context_is_defined_in_plugin_module() -> None:
    assert TranspilerContext.__module__ == "transpiler_mate.api.plugin"


def test_transpiler_context_is_an_immutable_pydantic_model() -> None:
    process = cast("object", object())
    context = TranspilerContext.model_construct(
        source=Path("workflow.cwl"),
        document=(process,),
        metadata=object(),
    )

    assert context.processes == (process,)
    with pytest.raises(ValidationError, match="Instance is frozen"):
        context.source = Path("changed.cwl")
    assert isinstance(context, BaseModel)


@pytest.mark.parametrize(
    "source",
    [
        "http://example.com/workflow.cwl",
        "https://example.com/workflow.cwl",
        "oci://registry.example.com/workflows/example:latest",
        "file:///tmp/workflow.cwl",
        "s3://bucket/workflow.cwl",
    ],
)
def test_transpiler_context_accepts_url_sources(source: str) -> None:
    url = AnyUrl(source)

    context = TranspilerContext(
        source=url,
        document=Workflow(inputs=[], outputs=[], steps=[]),
        metadata=SoftwareApplication.model_construct(),
    )

    assert context.source == url
