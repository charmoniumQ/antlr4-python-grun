from pathlib import Path
import os
import pytest
import itertools
import antlr4_grun.lib as lib


project_dir = Path(__file__).parent.parent.relative_to(os.getcwd())
json_grammar_path = project_dir / "tests" / "sample" / "JSON.g4"
json_source_path = project_dir / "tests" / "sample" / "source.json"


def test_parse() -> None:
    lib.parse(json_grammar_path, "json", json_source_path)
