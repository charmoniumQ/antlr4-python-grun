import re
from pathlib import Path
import subprocess
import tempfile
import pytest
from typer.testing import CliRunner
from antlr4_grun.main import app

@pytest.fixture
def compiled_json_grammer_path(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(app, [
        "compile",
        "tests/sample/JSON.g4",
        "--output-dir",
        str(tmp_path),
    ])
    assert result.exit_code == 0, result.output
    yield tmp_path

def test_tokenize(compiled_json_grammer_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(app, [
        "tokenize",
        "JSON",
        "--location",
        compiled_json_grammer_path,
        "tests/sample/source.json",
    ])
    assert result.exit_code == 0, result.output
    print(str(result.output))



@pytest.mark.parametrize("pretty", [True, False])
def test_parse(compiled_json_grammer_path: Path, pretty: bool) -> None:
    runner = CliRunner()
    result = runner.invoke(app, [
        "parse",
        "JSON",
        "json",
        "--location",
        compiled_json_grammer_path,
        "tests/sample/source.json",
        *(["--ugly"] if not pretty else [])
    ])
    assert result.exit_code == 0, result.output
    if pretty:
        output = re.sub(r"\s+", " ", result.output)
    else:
        output = result.output
        print(repr(output))
