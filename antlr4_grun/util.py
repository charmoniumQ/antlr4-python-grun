import sys
from pathlib import Path
import contextlib
import collections
from typing import TypeVar, List

Value = TypeVar("Value")


class DotDict(collections.UserDict[str, Value]):
    """Dict that is accessible through dot-notation (like JavaScript)."""
    data = {}
    def __getattr__(self, attr: str) -> Value:
        return self.data[attr]
    def __setattr__(self, attr: str, value: Value) -> None:
        self.data[attr] = value
    def __delattr__(self, attr: str) -> None:
        del self.data[attr]


@contextlib.contextmanager
def sys_path_prepend(paths: List[Path]) -> None:
    sys.path = list(map(str, paths)) + sys.path
    yield
    sys.path = sys.path[len(paths):]
