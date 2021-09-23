import traceback
import re
from pathlib import Path
import subprocess
import itertools
import tempfile
import os
from typing import Iterator
import pytest
from typer.testing import CliRunner
import json
from antlr4_grun.cli import app


project_dir = Path(__file__).parent.parent.relative_to(os.getcwd())
json_grammar_path = project_dir / "tests" / "sample" / "JSON.g4"
json_source_path = project_dir / "tests" / "sample" / "source.json"


@pytest.mark.parametrize("format", ["json", "s-expr"])
def test_tokenize(format: str) -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "tokenize",
            str(json_grammar_path),
            "--format",
            format,
            str(json_source_path),
        ],
    )
    assert not result.exception, traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0, result.output


@pytest.mark.parametrize("pretty,format", itertools.product([True, False], ["json", "s-expr"]))
def test_parse(pretty: bool, format: str) -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "parse",
            str(json_grammar_path),
            "json",
            "--format",
            format,
            str(json_source_path),
            *(["--ugly"] if not pretty else []),
        ],
    )
    assert not result.exception, traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0, result.output
    if format == "json":
        first_brace = result.output.index("{")
        json.loads(result.output[first_brace:])
