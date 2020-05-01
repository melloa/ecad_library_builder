import logging
import pytest
import pickle
import sys
import os

from example_symbol_parser import get_layouts
from symbol_parser import SymbolParser, LOG


class Truth:
    class LM3100:
        VARIABLE = "lm3100.pkl"
        PIN_COUNT = 20
        OUTLINE = (247.6789, 119.5301, 305.6109, 207.5301)

    class AS1115:
        VARIABLE = "AS1115_DS000206_1-00.pkl"
        PIN_COUNT = 10
        OUTLINE = (189.35999999999999, 108.47999999999999, 259.8, 236.76)


class TestSymbolParser:
    def setup(self):
        self.testdata = os.getcwd().split("ecad_library_builder")[0]
        self.testdata += "ecad_library_builder/symbol/testdata/"
        self.sp = SymbolParser()
        LOG.setLevel(level=logging.WARNING)

    def _verify_component(self, component):
        data = None
        var_path = self.testdata + component.VARIABLE
        with open(var_path, "rb") as f:
            data = pickle.load(f)

        symbol = self.sp.parse(data)
        rect = symbol.x0, symbol.y0, symbol.x1, symbol.y1

        assert len(symbol.pins) == component.PIN_COUNT
        assert len(symbol.text) == component.PIN_COUNT + 1
        assert rect == component.OUTLINE

    def test_lm3100(self):
        self._verify_component(Truth.LM3100)

    def test_as1115(self):
        data = None
        var_path = self.testdata + Truth.AS1115.VARIABLE
        with open(var_path, "rb") as f:
            data = pickle.load(f)

        symbol = self.sp.parse(data)
        rect = symbol.x0, symbol.y0, symbol.x1, symbol.y1

        assert rect == Truth.AS1115.OUTLINE


if __name__ == "__main__":
    if "ecad_library_builder" not in os.getcwd():
        raise RuntimeError("Need to call test from within the Git repo")

    current_path = os.path.dirname(os.path.realpath(__file__))
    sys.exit(pytest.main(["-v", current_path]))
