import enum
import json
import importlib
import subprocess
import shutil
from pathlib import Path
import os
from typing import Tuple, Iterable
import antlr4  # type: ignore
from . import util


class FormatType(str, enum.Enum):
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
        else:
            raise NotImplementedError()

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
            return f"]}}"
        else:
            raise NotImplementedError()


def get_cache_path() -> Path:
    path = (
        Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
        / "antlr4-python-grun"
    )
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_antlr_jar() -> Path:
    antlr_jar_path = get_cache_path() / "antlr-4.8-complete.jar"
    if not antlr_jar_path.exists():
        antlr_url = "https://www.antlr.org/download/antlr-4.8-complete.jar"
        util.download(antlr_url, antlr_jar_path)
    return antlr_jar_path


def compile(grammar_path: Path) -> Path:
    name = grammar_path.stem
    build_dir = get_cache_path() / name
    antlr_jar = get_antlr_jar()
    representative_file = build_dir / f"{name}Lexer.py"
    if (
        not representative_file.exists()
        or representative_file.stat().st_mtime < grammar_path.stat().st_mtime
    ):
        if build_dir.exists():
            shutil.rmtree(build_dir)
        build_dir.mkdir()
        subprocess.run(
            [
                "java",
                "-jar",
                str(antlr_jar),
                "-o",
                str(build_dir),
                "-Dlanguage=Python3",
                "-no-listener",
                str(grammar_path.name),
            ],
            check=True,
            cwd=grammar_path.parent,
        )
    return build_dir


def get_lexer_parser(grammar_path: Path) -> Tuple[antlr4.Lexer, antlr4.Parser]:
    build_dir = compile(grammar_path)
    name = grammar_path.stem
    with util.sys_path_prepend([build_dir]):
        return (
            getattr(
                importlib.import_module(f"{name}Lexer", package=None),
                f"{name}Lexer",
            ),
            getattr(
                importlib.import_module(f"{name}Parser", package=None),
                f"{name}Parser",
            ),
        )


def tokenize(
    grammar: Path,
    input: Path,
) -> Iterable[str]:
    Lexer, _ = get_lexer_parser(grammar)
    input_stream = antlr4.FileStream(input)
    lexer = Lexer(input_stream)
    while True:
        token = lexer.nextToken()
        yield token
        if token.type == token.EOF:
            break


def parse(
    grammar: Path,
    initial_rule: str,
    input: Path,
) -> antlr4.ParserRuleContext:
    Lexer, Parser = get_lexer_parser(grammar)
    input_stream = antlr4.FileStream(input)
    lexer = Lexer(input_stream)
    stream = antlr4.CommonTokenStream(lexer)
    parser = Parser(stream)
    return getattr(parser, initial_rule)()


def format_tree(
    root: antlr4.ParserRuleContext,
    pretty: bool,
    format: FormatType,
) -> str:
    stack = [(root, True)]
    depth = 0
    buf = []
    while stack:
        node, last = stack.pop()
        if node == "end":
            depth -= 1
            buf.append(depth * " " if pretty else "")
            buf.append(format.exit_rule())
            if not last:
                buf.append(format.sibling_sep())
        elif isinstance(node, antlr4.tree.Tree.TerminalNodeImpl):
            buf.append(depth * " " if pretty else "")
            buf.append(format.format_token(node.symbol))
            if not last:
                buf.append(format.sibling_sep())
        else:
            buf.append(depth * " " if pretty else "")
            buf.append(format.enter_rule(node))
            depth += 1
            children = [] if node.children is None else node.children
            stack.append(("end", last))
            stack.extend(util.first_sentinel(list(children)[::-1]))
        if pretty:
            buf.append("\n")
    return "".join(buf)
