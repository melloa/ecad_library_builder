from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import argparse

from symbol_parser import SymbolParser


def get_layouts(path):
    f = open(path, "rb")
    parser = PDFParser(f)
    document = PDFDocument(parser)
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    layouts = []
    for page in PDFPage.create_pages(document):
        interpreter.process_page(page)
        layouts.append(device.get_result())

    f.close()
    return layouts


def plot(axis_limits, symbol):
    fig, ax = plt.subplots(1)

    x0, y0, x1, y1 = symbol.rectangle.bbox
    rect = patches.Rectangle(
        (x0, y0), x1 - x0, y1 - y0, linewidth=1, edgecolor="r", facecolor="none"
    )
    ax.add_patch(rect)

    for curve in symbol.curves:
        x = []
        y = []
        for pt in curve.pts:
            x.append(pt[0])
            y.append(pt[1])
        ax.plot(x, y)

    for text in symbol.text:
        angle = 90 if text.vertical else 0
        start = text.x1 if text.vertical else text.x0
        ax.text(
            start,
            text.y0,
            str(text),
            fontsize=12,
            rotation=angle,
            rotation_mode="anchor",
            family="monospace",
        )
    xmin, ymin, xmax, ymax = axis_limits
    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)
    plt.show()


parser = argparse.ArgumentParser()
parser.add_argument("path", help="Path to a PDF")
args = parser.parse_args()


# Script starts here
layouts = get_layouts(args.path)

# I don't think there's a clean way to access inner object
# except for using the private variable or iterating
# 34 is hardcoded for the example circuit to get the symbol
# Only works for LM3100
symbol_figure = layouts[0]._objs[34]
symbol = SymbolParser().parse(symbol_figure)

# Plots the contents of symbol_figure
# plot(layouts[0].bbox, symbol_figure._objs)

plot(symbol_figure.bbox, symbol)
