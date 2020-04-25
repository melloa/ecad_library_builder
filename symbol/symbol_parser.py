from pdfminer.layout import LTCurve, LTChar, LTRect
import logging

MAXIMUM_DIST_TO_NEXT_CHAR = 1.0  # pixels ?
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


class Symbol:
    def __init__(self, rectangle):
        self.x0, self.y0, self.x1, self.y1 = rectangle.bbox
        self.text = []
        self.curves = []
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

    def within(self, target):
        return (
            self.x0 <= target.x0
            and self.y0 <= target.y0
            and self.x1 >= target.x1
            and self.y1 >= target.y1
        )


class SymbolParser:
    def parse(self, figure):
        def area(rect):
            return (rect.x1 - rect.x0) * (rect.y1 - rect.y0)

        LOG.info("Starting symbol parser")
        # Get largest rectangle
        # TODO: What if not a LTRect?
        areas_of_rects = [area(o) if type(o) == LTRect else 0 for o in figure]
        index = areas_of_rects.index(max(areas_of_rects))
        # TODO: Add proper support for indexing sub-objects
        symbol = Symbol(figure._objs[index])
        LOG.info("Created symbol based on largest rectangle")
        objects_within_symbol = [o for o in figure if symbol.within(o)]
        characters = [o for o in objects_within_symbol if type(o) == LTChar]
        rectangles = [o for o in objects_within_symbol if type(o) == LTRect]
        curves = [o for o in objects_within_symbol if type(o) == LTCurve]
        characters.reverse()

        # TODO: Fix me
        if len(rectangles) > 1:
            LOG.warn(
                "More than one rectangle for symbol! Found {}".format(len(rectangles))
            )
        symbol.add_rectangle(rectangles[0])
        # TODO: Fix me - better naming
        symbol.add_curves(curves)

        total_processed = len(characters) + len(rectangles) + len(curves)
        if total_processed != len(objects_within_symbol):
            LOG.warn("Not all objects processed!")

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
