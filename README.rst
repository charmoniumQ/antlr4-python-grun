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
