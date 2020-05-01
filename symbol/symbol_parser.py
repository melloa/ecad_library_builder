from pdfminer.layout import LTCurve, LTChar, LTRect, LTLine
import numpy as np
import logging

MAXIMUM_DIST_TO_NEXT_CHAR = 1.0  # pixels ?
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


class Symbol:
    def __init__(self, rectangle):
        self.x0, self.y0, self.x1, self.y1 = rectangle.bbox
        self.text = []
        self.curves = []
        self.pins = []
        self.pin_width = 0
        self.rectangle = None

    def add_text(self, text):
        LOG.info("Adding text of type: {}".format(type(text)))
        if type(text) == list:
            self.text.extend(text)
        elif type(text) == TextLine:
            self.text.append(text)
        else:
            ValueError(
                "Unknown type attempting to add as text! ({})".format(type(text))
            )

    def add_curves(self, curves):
        LOG.info("Adding curves of type: {}".format(type(curves)))
        if type(curves) == list:
            self.curves.extend(curves)
        elif type(curves) == LTCurve:
            self.curves.append(curves)
        else:
            ValueError(
                "Unknown type attempting to add as curves! ({})".format(type(curves))
            )

    def add_rectangle(self, rect):
        LOG.info("Adding rectangle: {}".format(type(rect)))
        if type(rect) == LTRect:
            self.rectangle = rect
        else:
            ValueError(
                "Unknown type attempting to add as a rectangle! ({})".format(type(rect))
            )

    def add_pin(self, pin):
        LOG.info("Adding pin: {}".format(type(pin)))
        if type(pin) == LTLine:
            self.pin_width = pin.width
            self.pins.append(pin)
        else:
            ValueError(
                "Unknown type attempting to add as a rectangle! ({})".format(type(pin))
            )

    def within(self, target):
        return (
            self.x0 <= target.x0
            and self.y0 <= target.y0
            and self.x1 >= target.x1
            and self.y1 >= target.y1
        )

    def touching(self, line):
        diffs = [
            abs(line.x0 - self.x0),
            abs(line.x1 - self.x0),
            abs(line.x0 - self.x1),
            abs(line.x1 - self.x1),
            abs(line.y0 - self.y0),
            abs(line.y1 - self.y0),
            abs(line.y0 - self.y1),
            abs(line.y1 - self.y1),
        ]

        return any([diff < 1 for diff in diffs])

    def width(self):
        return self.x1 - self.x0

    def height(self):
        return self.y1 - self.y0


def area(rect):
    return (rect.x1 - rect.x0) * (rect.y1 - rect.y0)


class SymbolParser:
    # TUNABLE PARAMETERS
    # TODO: Convert to numpy for matrix math
    _find_part_weights = (
        0.1,  # Number of objects within
        0.1,  # Number of objects touching
        300,  # Height / width ratio
        0.01,  # Area
    )

    def find_part(self):
        algorithms = [self._find_part_largest_rectangle]
        result = []
        for function in algorithms:
            result.extend(function(n=3))
        print(result)
        return sorted(result, key=lambda r: r[0], reverse=True)[0]

    def _find_part_largest_rectangle(self, n=1):
        symbols = []
        areas_of_rects = []
        for object_ in self._figure:
            if type(object_) == LTRect:
                areas_of_rects.append(area(object_))
            else:
                areas_of_rects.append(0)

        available_rects = self._figure._objs
        while len(symbols) < n:
            index = areas_of_rects.index(max(areas_of_rects))
            # TODO: Add proper support for indexing sub-objects
            symbol = Symbol(available_rects[index])
            symbols.append((self._find_part_cost(symbol), symbol))
            areas_of_rects.pop(index)
            available_rects.pop(index)

        return symbols

    def _find_part_cost(self, symbol):
        if symbol.height() < 2 or symbol.width() < 2:
            return 0

        within = [obj for obj in self._figure if symbol.within(obj)]
        touching = [obj for obj in self._figure if symbol.touching(obj)]
        ratio = symbol.height() / symbol.width()
        area = symbol.height() * symbol.width()

        # TODO: Convert to matrix math
        cost = self._find_part_weights[0] * len(within)
        cost += self._find_part_weights[1] * len(touching)
        cost += self._find_part_weights[2] * ratio
        cost += self._find_part_weights[3] * area

        # TODO: Build formatted cost table outputter
        LOG.debug(
            "-----> {}  - {}x{} = {} ".format(
                cost, symbol.height(), symbol.width(), ratio
            )
        )
        return cost

    def parse(self, figure):
        LOG.info("Starting symbol parser")
        self._figure = figure
        (cost, symbol) = self.find_part()

        LOG.info("Created symbol with cost of {}".format(cost))
        objects_within_symbol = [o for o in figure if symbol.within(o)]
        lines = [o for o in figure if type(o) == LTLine]
        characters = [o for o in objects_within_symbol if type(o) == LTChar]
        rectangles = [o for o in objects_within_symbol if type(o) == LTRect]
        curves = [o for o in objects_within_symbol if type(o) == LTCurve]
        characters.reverse()

        # TODO: Fix me
        if len(rectangles) > 1:
            LOG.warning(
                "More than one rectangle for symbol! Found {}".format(len(rectangles))
            )
        # symbol.add_rectangle(rectangles[0])
        # TODO: Fix me - better naming
        symbol.add_curves(curves)

        total_processed = len(characters) + len(rectangles) + len(curves)
        if total_processed != len(objects_within_symbol):
            LOG.warning("Not all objects processed!")

        textlines = []
        for _ in range(len(characters)):
            char = characters.pop()
            new = True
            for tl in textlines:
                if tl.add(char):
                    new = False
                    break
            if new:
                textlines.append(TextLine(char))

        for line in lines:
            if symbol.touching(line):
                symbol.add_pin(line)

        symbol.add_text(textlines)
        LOG.info("Created textlines within symbol")
        LOG.info("Done.")
        return symbol


class TextLine:
    def __init__(self, character):
        self.x0, self.y0, self.x1, self.y1 = character.bbox
        self.vertical = not character.upright
        self.line = self.x0 if self.vertical else self.y0
        self.position = self.y1 if self.vertical else self.x1
        self.text = character.get_text()
        self._initial_character = character

    def __str__(self):
        return self.text

    def add(self, char):
        # Check to see if on the same line
        line = char.x0 if self.vertical else char.y0
        position = char.y0 if self.vertical else char.x0
        next_position = char.y1 if self.vertical else char.x1
        if line != self.line:
            return False

        # Check if it's the next character
        # TODO: Add support for whitespace
        # TODO: Add support for out-of-order characters
        if abs(position - self.position) > MAXIMUM_DIST_TO_NEXT_CHAR:
            return False

        self.text += char.get_text()
        self.position = next_position
        return True
