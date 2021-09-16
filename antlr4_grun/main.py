import subprocess
import urllib.request
import shutil
import importlib
from pathlib import Path
import json
from typing import Optional, Tuple, Any
import typer
import antlr4
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


@app.command(help="""Tokenize the input. Each line is formatted as:

    RULE_NAME "json-encoded string containing lexeme"

""")
def tokenize(
        grammar: str = typer.Argument(
            ...,
            help="Base name of compiled grammar"
        ),
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
) -> None:
    Lexer, _ = get_lexer_parser(location, grammar)
    input_stream = antlr4.FileStream(input)
    lexer = Lexer(input_stream)
    token_type_map = {
        symbolic_id + len(lexer.literalNames) - 1: symbolic_name
        for symbolic_id, symbolic_name in enumerate(lexer.symbolicNames)
    }
    while True:
        token = lexer.nextToken()
        type_ = token_type_map.get(token.type, "literal")
        print(f"{type_} {json.dumps(token.text)}")
        if token.type == token.EOF:
            break


@app.command(help="""Print parse of input as an S-expression tree.""")
def parse(
        grammar: str = typer.Argument(
            ...,
            help="Base name of compiled grammar"
        ),
        initial_rule: str = typer.Argument(
            ...,
            help="Initial rule to start parsing from"
        ),
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
        pretty: bool = typer.Option(True, " /--ugly")
) -> None:
    Lexer, Parser = get_lexer_parser(location, grammar)
    input_stream = antlr4.FileStream(input)
    lexer = Lexer(input_stream)
    stream = antlr4.CommonTokenStream(lexer)
    parser = Parser(stream)

    end = "\n" if pretty else " "

    stack = [getattr(parser, initial_rule)()]
    depth = 0
    while stack:
        node = stack.pop()
        prefix = depth * " " if pretty else ""
        if isinstance(node, antlr4.tree.Tree.TerminalNodeImpl):
            print(f"{prefix}{json.dumps(node.getText())}", end=end)
        elif isinstance(node, str):
            depth -= 1
            print(f"{prefix[:-1]})", end=end)
        else:
            rule_name = Parser.ruleNames[node.getRuleIndex()]
            if node.children:
                print(f"{prefix}({rule_name}", end=end)
                stack.append("end")
                stack.extend(node.children[::-1])
                depth += 1
            else:
                print(f"{prefix}({rule_name})", end=end)


@app.command(help="""Compiles the grammar with antlr4
This requires a JRE.
""")
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
    subprocess.run([
        "java",
        "-jar",
        str(antlr_path),
        "-o",
        str(output_dir),
        "-Dlanguage=Python3",
        "-no-listener",
        # *options,
        grammar_path.name,
    ], check=True, cwd=grammar_path.parent)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
