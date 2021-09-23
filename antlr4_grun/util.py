import sys
from pathlib import Path
import contextlib
import collections
import shutil
import urllib.request
from typing import TypeVar, List, Iterator, Tuple, Iterable

Value = TypeVar("Value")


class DotDict(collections.UserDict[str, Value]):
    """Dict that is accessible through dot-notation (like JavaScript)."""

    data: dict[str, Value] = {}

    def __getattr__(self, attr: str) -> Value:
        return self.data[attr]

    def __setattr__(self, attr: str, value: Value) -> None:
        self.data[attr] = value

    def __delattr__(self, attr: str) -> None:
        del self.data[attr]


def first_sentinel(iterable: Iterable[Value]) -> Iterator[Tuple[Value, bool]]:
    iterator = iter(iterable)
    yield (next(iterator), True)
    for elem in iterator:
        yield (elem, False)


def download(url: str, dest_path: Path) -> None:
    webreq = urllib.request.urlopen(url)
    with dest_path.open("wb") as dest:
        shutil.copyfileobj(webreq, dest)


@contextlib.contextmanager
def sys_path_prepend(paths: List[Path]) -> Iterator[None]:
    sys.path = list(map(str, paths)) + sys.path
    yield
    sys.path = sys.path[len(paths) :]
