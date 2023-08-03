Pure-Python replacement of the `antlr <https://www.antlr.org/>`__ test
rig, ``org.antlr.v4.gui.TestRig`` (aka ``grun``).

There are a few places this executable differs in the interest of better
or more Pythonic design. For example,

-  I use `click <https://click.palletsprojects.com/en/8.0.x/>`__'s
   conventions for CLI argument parsing, which have a double-dash for
   long-options, rather than Java's convention, which have a
   single-dash.

-  I use JSON strings to escape source lexemes. This is more elegant and
   is easily parsed in whatever next phase of processing exists.

# Usage

```
$ pip install https://github.com/charmoniumQ/antlr4-python-grun/archive/main.tar.gz

$ pygrun parse --help
Usage: pygrun parse [OPTIONS] GRAMMAR INITIAL_RULE [INPUT]

  Print parse of input as tree.

Arguments:
  GRAMMAR       [required]
  INITIAL_RULE  Initial rule to start parsing from  [required]
  [INPUT]       [default: /dev/stdin]

Options:
   / --ugly               [default: True]
  --format [s-expr|json]  [default: FormatType.s_expr]
  --help                  Show this message and exit.

$ pygrun tokenize --helpUsage: pygrun tokenize [OPTIONS] GRAMMAR [INPUT]

  Tokenize the input.

Arguments:
  GRAMMAR  [required]
  [INPUT]  [default: /dev/stdin]

Options:
  --format [s-expr|json]  [default: FormatType.s_expr]
  --help                  Show this message and exit.
```
