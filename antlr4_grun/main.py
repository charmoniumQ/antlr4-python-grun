from enum import Enum
import subprocess
import urllib.request
import shutil
import sys
import importlib
from pathlib import Path
import json
from typing import Optional, Tuple, Any
import typer
import antlr4  # type: ignore

# https://github.com/antlr/antlr4/blob/master/doc/python-target.md
from . import util


def get_lexer_parser(location: Path, grammar: str) -> Tuple[Any, Any]:
    with util.sys_path_prepend([location]):
        return (
            getattr(
                importlib.import_module(f"{grammar}Lexer", package=None),
                f"{grammar}Lexer",
            ),
            getattr(
                importlib.import_module(f"{grammar}Parser", package=None),
                f"{grammar}Parser",
            ),
        )


app = typer.Typer()


class FormatType(str, Enum):
    s_expr = "s-expr"
    json = "json"

    def format_token(self, token: antlr4.Token) -> str:
        lexer = token.getTokenSource()
        token_type_map = {
            symbolic_id + len(lexer.literalNames) - 1: symbolic_name
            for symbolic_id, symbolic_name in enumerate(lexer.symbolicNames)
        }
        type_ = token_type_map.get(token.type, "literal")
        if self == FormatType.s_expr:
            return f"({type_} {json.dumps(token.text)})"
        elif self == FormatType.json:
            return json.dumps(
                dict(
                    type=type_,
                    text=token.text,
                    line=token.line,
                    column=token.column,
                )
            )
        else:
            raise NotImplementedError("Format type {self!s} is not implemented")

    def sibling_sep(self) -> str:
        if self == FormatType.s_expr:
            return " "
        elif self == FormatType.json:
            return ","

    def enter_rule(self, ctx: antlr4.ParserRuleContext) -> str:
        rule_name = ctx.parser.ruleNames[ctx.getRuleIndex()]
        if self == FormatType.s_expr:
            return f"({rule_name}"
        elif self == FormatType.json:
            return f'{{"rule": {json.dumps(rule_name)}, "children": ['
        else:
            raise NotImplementedError()

    def exit_rule(self) -> str:
        if self == FormatType.s_expr:
            return f")"
        elif self == FormatType.json:
            return f']}}'
        else:
            raise NotImplementedError()


@app.command(help="Tokenize the input.")
def tokenize(
    grammar: str = typer.Argument(..., help="Base name of compiled grammar"),
    input: str = typer.Argument(
        "/dev/stdin",
        exists=True,
        file_okay=True,
        readable=True,
    ),
    location: Path = typer.Option(
        ".",
        exists=True,
        dir_okay=True,
        help="Location of compiled grammar",
    ),
    format: FormatType = FormatType.s_expr,
) -> None:
    Lexer, _ = get_lexer_parser(location, grammar)
    input_stream = antlr4.FileStream(input)
    lexer = Lexer(input_stream)
    while True:
        token = lexer.nextToken()
        print(format.format_token(token))
        if token.type == token.EOF:
            break


@app.command(help="""Print parse of input as tree.""")
def parse(
    grammar: str = typer.Argument(..., help="Base name of compiled grammar"),
    initial_rule: str = typer.Argument(..., help="Initial rule to start parsing from"),
    input: str = typer.Argument(
        "/dev/stdin",
        exists=True,
        file_okay=True,
        readable=True,
    ),
    location: Path = typer.Option(
        ".",
        exists=True,
        dir_okay=True,
        help="Location of compiled grammar",
    ),
    pretty: bool = typer.Option(True, " /--ugly"),
    format: FormatType = FormatType.s_expr,
) -> None:
    Lexer, Parser = get_lexer_parser(location, grammar)
    input_stream = antlr4.FileStream(input)
    lexer = Lexer(input_stream)
    stream = antlr4.CommonTokenStream(lexer)
    parser = Parser(stream)

    stack = [(getattr(parser, initial_rule)(), True)]
    depth = 0
    while stack:
        node, last = stack.pop()
        if node == "end":
            depth -= 1
            sys.stdout.write(depth * " " if pretty else "")
            sys.stdout.write(format.exit_rule())
            if not last:
                sys.stdout.write(format.sibling_sep())
        elif isinstance(node, antlr4.tree.Tree.TerminalNodeImpl):
            sys.stdout.write(depth * " " if pretty else "")
            sys.stdout.write(format.format_token(node.symbol))
            if not last:
                sys.stdout.write(format.sibling_sep())
        else:
            sys.stdout.write(depth * " " if pretty else "")
            sys.stdout.write(format.enter_rule(node))
            depth += 1
            children = [] if node.children is None else node.children
            stack.append(("end", last))
            stack.extend(util.first_sentinel(list(children)[::-1]))
        if pretty:
            sys.stdout.write("\n")


@app.command(
    help="""Compiles the grammar with antlr4
This requires a JRE.
"""
)
def compile(
    grammar_path: Path = typer.Argument(
        ...,
        help="Base name of the to-be compiled grammar",
        exists=True,
        file_okay=True,
        readable=True,
    ),
    output_dir: str = typer.Option(
        ".",
        exists=True,
        dir_okay=True,
    ),
    antlr_path: Optional[Path] = typer.Option(
        None,
        exists=True,
        file_okay=True,
        help="Path to antlr JAR. If not set, I will download and store a fresh copy.",
    ),
) -> None:
    if antlr_path is None:
        antlr_path = Path("/tmp/antlr-4.9.2-complete.jar")
        if not antlr_path.exists():
            antlr_url = "https://www.antlr.org/download/antlr-4.9.2-complete.jar"
            antlr_webreq = urllib.request.urlopen(antlr_url)
            with antlr_path.open("wb") as antlr_dest:
                shutil.copyfileobj(antlr_webreq, antlr_dest)
    subprocess.run(
        [
            "java",
            "-jar",
            str(antlr_path),
            "-o",
            str(output_dir),
            "-Dlanguage=Python3",
            "-no-listener",
            # *options,
            grammar_path.name,
        ],
        check=True,
        cwd=grammar_path.parent,
    )


def main() -> None:
    app()


if __name__ == "__main__":
    main()
