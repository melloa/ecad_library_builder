from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
from random import random

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import argparse
import os

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
    _, ax = plt.subplots(1)

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

    for pin in symbol.pins:
        x = [pin.bbox[0], pin.bbox[2]]
        y = [pin.bbox[1], pin.bbox[3]]
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


def plot_bbox(axis_limits, bboxs):
    _, ax = plt.subplots(1)

    for r in bboxs:
        x0, y0, x1, y1 = r.bbox
        c = (random(), random(), random(), 0.7)
        rect = patches.Rectangle(
            (x0, y0), x1 - x0, y1 - y0, linewidth=1, edgecolor=c, facecolor="none"
        )
        ax.add_patch(rect)
    xmin, ymin, xmax, ymax = axis_limits
    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)
    plt.show()


parser = argparse.ArgumentParser()
parser.add_argument("path", help="Path to a PDF")
parser.add_argument("--plot_page", action="store_true")
parser.add_argument("--plot_figure", action="store_true")
parser.add_argument("--plot_symbol", action="store_true")
args = parser.parse_args()

if not os.path.exists(args.path):
    raise RuntimeError("File doesn't exist!")

filename = os.path.basename(args.path)

symbol_location = {
    "lm3100.pdf": {"page": 0, "object": 34},
    "AS1115_DS000206_1-00.pdf": {"page": 1, "object": None},
    "74HC_HCT165.pdf": {"page": 1, "object": None},
}

if filename not in symbol_location:
    raise RuntimeError(
        "Example script doesn't work on that datasheet yet!\n\nTry on:\n{}".format(
            list(symbol_location.keys())
        )
    )

# Script starts here
layouts = get_layouts(args.path)

# I don't think there's a clean way to access inner object
# except for using the private variable or iterating
# 34 is hardcoded for the example circuit to get the symbol
# Only works for LM3100
symbol_page = layouts[symbol_location[filename]["page"]]

if args.plot_page:
    plot_bbox(symbol_page.bbox, symbol_page._objs)

symbol_figure = symbol_page
if symbol_location[filename]["object"]:
    symbol_figure = symbol_page._objs[symbol_location[filename]["object"]]

symbol = SymbolParser().parse(symbol_figure)

# Plots the contents of symbol_figure
if args.plot_figure:
    plot_bbox(symbol_page.bbox, symbol_figure._objs)

if args.plot_symbol:
    plot(symbol_figure.bbox, symbol)
