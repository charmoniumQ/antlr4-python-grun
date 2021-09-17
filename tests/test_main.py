import re
from pathlib import Path
import subprocess
import itertools
import tempfile
from typing import Iterator
import pytest
from typer.testing import CliRunner
import json
from antlr4_grun.main import app


@pytest.fixture(scope="session")
def compiled_json_grammer_path(tmp_path_factory: pytest.TempPathFactory) -> Iterator[Path]:
    runner = CliRunner()
    tmp_path = tmp_path_factory.mktemp("build")
    result = runner.invoke(
        app,
        [
            "compile",
            "tests/sample/JSON.g4",
            "--output-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0, result.output
    yield tmp_path


@pytest.mark.parametrize("format", ["json", "s-expr"])
def test_tokenize(compiled_json_grammer_path: Path, format: str) -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "tokenize",
            "JSON",
            "--location",
            str(compiled_json_grammer_path),
            "--format",
            format,
            "tests/sample/source.json",
        ],
    )
    assert result.exit_code == 0, result.output
    print(str(result.output))


@pytest.mark.parametrize("pretty,format", itertools.product([True, False], ["json", "s-expr"]))
def test_parse(compiled_json_grammer_path: Path, pretty: bool, format: str) -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "parse",
            "JSON",
            "json",
            "--location",
            str(compiled_json_grammer_path),
            "--format",
            format,
            "tests/sample/source.json",
            *(["--ugly"] if not pretty else []),
        ],
    )
    assert result.exit_code == 0, result.output
    if format == "json":
        first_brace = result.output.index("{")
        json.loads(result.output[first_brace:])
