import sys
from pathlib import Path
from typing import Optional, Tuple, Any
import typer
import antlr4  # type: ignore

# https://github.com/antlr/antlr4/blob/master/doc/python-target.md
from . import lib
from . import util


app = typer.Typer()


@app.command(help="Tokenize the input.")
def tokenize(
    grammar: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    input: Path = typer.Argument(
        "/dev/stdin",
        exists=True,
        file_okay=True,
        readable=True,
    ),
    format: lib.FormatType = lib.FormatType.s_expr,
) -> None:
    for token in lib.tokenize(grammar, input):
        print(format.format_token(token))


@app.command(help="""Print parse of input as tree.""")
def parse(
    grammar: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    initial_rule: str = typer.Argument(..., help="Initial rule to start parsing from"),
    input: str = typer.Argument(
        "/dev/stdin",
        exists=True,
        file_okay=True,
        readable=True,
    ),
    pretty: bool = typer.Option(True, " /--ugly"),
    format: lib.FormatType = lib.FormatType.s_expr,
) -> None:
    root = lib.parse(grammar, initial_rule, input)
    print(lib.format_tree(root, pretty, format))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
