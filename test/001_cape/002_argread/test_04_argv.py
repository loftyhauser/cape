
import sys

import argread


def test_readkeys01():
    sys.argv = ["p", "-cj"]
    a, kw = argread.readkeys()
    assert a == []
    assert kw == {
        "cj": True,
        "__replaced__": [],
    }

