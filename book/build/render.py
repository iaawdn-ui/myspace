"""
Professional PDF renderer for CAC. 701 Fundamentals of Counseling Theories.

Design notes
------------
* Custom 7.5 x 10 in page with mirrored (gutter-aware) margins achieved
  through dynamic frame padding on alternating pages.
* Serif body face (STIXGeneral) paired with a clean grotesque (DejaVuSans)
  for display type, captions and callout furniture.
* Multi-pass build resolves the table of contents, the list of figures, the
  list of tables and the back-of-book index to real page numbers.
* Running heads, full-bleed part dividers, illustrated chapter openers,
  styled callout boxes, banded tables and numbered figure/table captions.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Flowable, Frame, Image,
                                KeepTogether, NextPageTemplate, PageBreak,
                                Paragraph, PageTemplate, Spacer, Table,
                                TableStyle)
from reportlab.platypus.tableofcontents import SimpleIndex, TableOfContents

import mdparse
from mdparse import _inline as _mi

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CONTENT = os.environ.get("BOOK_CONTENT",
                         os.path.join(ROOT, "book", "content"))
FIGDIR = os.environ.get("BOOK_FIGURES", os.path.join(ROOT, "book", "figures"))
DIST = os.environ.get("BOOK_DIST", os.path.join(ROOT, "dist"))

WORD_TOTAL = 0

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------

NAVY = HexColor("#173A5E")
DEEP = HexColor("#0E2740")
ACCENT = HexColor("#A9741F")
TEAL = HexColor("#1F6F6B")
PLUM = HexColor("#6B3E75")
CRIMSON = HexColor("#9B2C2C")
INK = HexColor("#1A1A1A")
SLATE = HexColor("#3F4A57")
MUTED = HexColor("#6B7684")
RULE = HexColor("#C9D2DB")
TINT = HexColor("#EEF2F6")
CREAM = HexColor("#FBF9F4")
WHITE = colors.white

# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------

import matplotlib  # noqa: E402

MPLFONTS = os.path.join(os.path.dirname(matplotlib.__file__), "mpl-data",
                        "fonts", "ttf")


def _reg(name, filename):
    pdfmetrics.registerFont(TTFont(name, os.path.join(MPLFONTS, filename)))


def register_fonts():
    _reg("BookSerif", "STIXGeneral.ttf")
    _reg("BookSerif-Bold", "STIXGeneralBol.ttf")
    _reg("BookSerif-Italic", "STIXGeneralItalic.ttf")
    _reg("BookSerif-BoldItalic", "STIXGeneralBolIta.ttf")
    _reg("BookSans", "DejaVuSans.ttf")
    _reg("BookSans-Bold", "DejaVuSans-Bold.ttf")
    _reg("BookSans-Oblique", "DejaVuSans-Oblique.ttf")
    pdfmetrics.registerFontFamily("BookSerif", normal="BookSerif",
                                  bold="BookSerif-Bold",
                                  italic="BookSerif-Italic",
                                  boldItalic="BookSerif-BoldItalic")
    pdfmetrics.registerFontFamily("BookSans", normal="BookSans",
                                  bold="BookSans-Bold",
                                  italic="BookSans-Oblique",
                                  boldItalic="BookSans-Bold")


register_fonts()

# ---------------------------------------------------------------------------
# Page geometry
# ---------------------------------------------------------------------------

PAGE_W, PAGE_H = 7.5 * inch, 10.0 * inch
OUTER = 0.78 * inch
GUTTER = 0.17 * inch
TOP = 0.82 * inch
BOT = 0.86 * inch
TEXT_W = PAGE_W - 2 * OUTER - GUTTER


def roman(n):
    vals = ((1000, "m"), (900, "cm"), (500, "d"), (400, "cd"), (100, "c"),
            (90, "xc"), (50, "l"), (40, "xl"), (10, "x"), (9, "ix"),
            (5, "v"), (4, "iv"), (1, "i"))
    out = ""
    for v, s in vals:
        while n >= v:
            out += s
            n -= v
    return out


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------

def make_styles():
    s = {}
    s["body"] = ParagraphStyle("body", fontName="BookSerif", fontSize=9.6,
                               leading=13.4, alignment=TA_JUSTIFY,
                               spaceAfter=0, textColor=INK, wordWrap="hyphen")
    s["lead"] = ParagraphStyle("lead", parent=s["body"], fontSize=10.5,
                               leading=15.0, textColor=DEEP, spaceAfter=7)
    s["h2"] = ParagraphStyle("h2", fontName="BookSans-Bold", fontSize=13.0,
                             leading=16.2, textColor=NAVY, spaceBefore=15,
                             spaceAfter=6, alignment=TA_LEFT)
    s["h3"] = ParagraphStyle("h3", fontName="BookSans-Bold", fontSize=10.8,
                             leading=13.8, textColor=TEAL, spaceBefore=11,
                             spaceAfter=4, alignment=TA_LEFT)
    s["h4"] = ParagraphStyle("h4", fontName="BookSans-Bold", fontSize=9.8,
                             leading=12.8, textColor=SLATE, spaceBefore=9,
                             spaceAfter=3, alignment=TA_LEFT)
    s["h5"] = ParagraphStyle("h5", fontName="BookSerif-Italic", fontSize=9.6,
                             leading=12.6, textColor=SLATE, spaceBefore=8,
                             spaceAfter=3)
    s["bullet"] = ParagraphStyle("bullet", parent=s["body"], leftIndent=13,
                                 bulletIndent=3, spaceAfter=3.0,
                                 alignment=TA_LEFT)
    s["bullet2"] = ParagraphStyle("bullet2", parent=s["bullet"], leftIndent=26,
                                  bulletIndent=16, spaceAfter=2.4)
    s["number"] = ParagraphStyle("number", parent=s["body"], leftIndent=18,
                                 bulletIndent=3, spaceAfter=3.8,
                                 alignment=TA_LEFT)
    s["number2"] = ParagraphStyle("number2", parent=s["number"],
                                  leftIndent=31, bulletIndent=17,
                                  spaceAfter=2.8)
    s["quote"] = ParagraphStyle("quote", parent=s["body"], fontSize=10.0,
                                leading=14.2, leftIndent=18, rightIndent=10,
                                textColor=DEEP, alignment=TA_LEFT,
                                spaceBefore=6, spaceAfter=9)
    s["figcap"] = ParagraphStyle("figcap", fontName="BookSans", fontSize=8.2,
                                 leading=10.8, textColor=SLATE,
                                 alignment=TA_LEFT, spaceBefore=5, spaceAfter=11)
    s["tblcap"] = ParagraphStyle("tblcap", fontName="BookSans", fontSize=8.2,
                                 leading=10.8, textColor=SLATE,
                                 alignment=TA_LEFT, spaceBefore=5, spaceAfter=11)
    s["tbl_head"] = ParagraphStyle("tbl_head", fontName="BookSans-Bold",
                                   fontSize=8.1, leading=10.3,
                                   textColor=WHITE, alignment=TA_LEFT)
    s["tbl_cell"] = ParagraphStyle("tbl_cell", fontName="BookSerif",
                                   fontSize=8.4, leading=10.9, textColor=INK,
                                   alignment=TA_LEFT)
    s["box_title"] = ParagraphStyle("box_title", fontName="BookSans-Bold",
                                    fontSize=8.9, leading=11.4, textColor=WHITE,
                                    alignment=TA_LEFT)
    s["box_body"] = ParagraphStyle("box_body", parent=s["body"],
                                   fontSize=9.1, leading=12.4, spaceAfter=3)
    s["box_bullet"] = ParagraphStyle("box_bullet", parent=s["box_body"],
                                     leftIndent=12, bulletIndent=2,
                                     spaceAfter=2.3)
    s["box_number"] = ParagraphStyle("box_number", parent=s["box_body"],
                                     leftIndent=15, bulletIndent=2,
                                     spaceAfter=2.5)
    s["box_h4"] = ParagraphStyle("box_h4", fontName="BookSans-Bold",
                                 fontSize=9.2, leading=12, textColor=DEEP,
                                 spaceBefore=4, spaceAfter=2)
    s["box_cont"] = ParagraphStyle("box_cont", fontName="BookSans-Bold",
                                   fontSize=8.4, leading=10.8, textColor=WHITE,
                                   alignment=TA_LEFT)
    s["fm_title"] = ParagraphStyle("fm_title", fontName="BookSans-Bold",
                                   fontSize=16.5, leading=20, textColor=DEEP,
                                   spaceAfter=4, spaceBefore=0)
    s["fm_h2"] = ParagraphStyle("fm_h2", fontName="BookSans-Bold",
                                fontSize=11.4, leading=14.8, textColor=NAVY,
                                spaceBefore=13, spaceAfter=5)
    s["fm_h3"] = ParagraphStyle("fm_h3", fontName="BookSans-Bold",
                                fontSize=9.9, leading=12.8, textColor=TEAL,
                                spaceBefore=9, spaceAfter=3)
    s["small"] = ParagraphStyle("small", parent=s["body"], fontSize=8.5,
                                leading=11.2)
    s["toc1"] = ParagraphStyle("toc1", fontName="BookSans-Bold", fontSize=9.7,
                               leading=13.6, textColor=DEEP, spaceBefore=8)
    s["toc2"] = ParagraphStyle("toc2", fontName="BookSerif", fontSize=9.0,
                               leading=12.0, textColor=INK, leftIndent=16)
    s["toc3"] = ParagraphStyle("toc3", fontName="BookSans", fontSize=8.5,
                               leading=11.4, textColor=MUTED, leftIndent=30)
    s["toc4"] = ParagraphStyle("toc4", fontName="BookSans", fontSize=8.2,
                               leading=10.8, textColor=MUTED, leftIndent=30)
    s["index_a"] = ParagraphStyle("index_a", fontName="BookSans-Bold",
                                  fontSize=9.2, leading=12.6, textColor=NAVY,
                                  spaceBefore=8, spaceAfter=3)
    s["index"] = ParagraphStyle("index", fontName="BookSerif", fontSize=8.5,
                                leading=10.8, textColor=INK, leftIndent=11,
                                firstLineIndent=-11, alignment=TA_LEFT)
    return s


ST = make_styles()

# ---------------------------------------------------------------------------
# Index term machinery
# ---------------------------------------------------------------------------

INDEX_RE = None
INDEX_MAP = {}


def load_index_terms(path):
    global INDEX_RE, INDEX_MAP
    INDEX_RE = None
    INDEX_MAP = {}
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    terms = data.get("terms", [])
    groups = []
    for t in terms:
        label = t.get("label") or t.get("term")
        variants = t.get("variants") or [label]
        groups.append((label, variants))
    groups.sort(key=lambda g: -max(len(v) for v in g[1]))
    pats = []
    for i, (label, variants) in enumerate(groups):
        alts = []
        for v in variants:
            alts.append(re.escape(v))
        pats.append("(?P<g%d>%s)" % (i, "(?:%s)s?" % "|".join(alts)))
        INDEX_MAP["g%d" % i] = label
    try:
        INDEX_RE = re.compile(r"\b(?:%s)\b" % "|".join(pats))
    except re.error:
        INDEX_RE = None


# ---------------------------------------------------------------------------
# Helper flowables
# ---------------------------------------------------------------------------

def _img_size(path):
    from reportlab.lib.utils import ImageReader
    if not path or not os.path.isfile(path):
        return (1, 1)
    return ImageReader(path).getSize()


def wrap_text(canvas, text, font, size, maxw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if canvas.stringWidth(trial, font, size) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


class Rule(Flowable):
    def __init__(self, width, thickness=0.6, color=RULE, space=6):
        Flowable.__init__(self)
        self._w = width
        self.thickness = thickness
        self.color = color
        self.space = space
        self.height = thickness + space

    def wrap(self, aw, ah):
        self._w = min(self._w, aw)
        self.width = self._w
        return (self._w, self.height)

    def draw(self):
        c = self.canv
        c.setStrokeColor(self.color)
        c.setLineWidth(self.thickness)
        c.line(0, self.space, self._w, self.space)


class FullBleedMixin(object):
    def _page_origin(self):
        ax, ay = self.canv.absolutePosition(0, 0)
        return ax, ay

    def _page_size(self):
        return self.canv._pagesize


class ChapterOpener(Flowable, FullBleedMixin):
    """Full-page illustrated chapter opener."""

    def __init__(self, number, title, subtitle, image, part_label, accent):
        Flowable.__init__(self)
        self.number = number
        self.title = title
        self.subtitle = subtitle
        self.image = image
        self.part_label = part_label
        self.accent = accent
        self.width = 0
        self.height = 0

    def wrap(self, aw, ah):
        self.width = aw
        self.height = ah
        return (aw, ah)

    def draw(self):
        c = self.canv
        aw, ah = self.width, self.height
        ax, ay = self._page_origin()
        pw, ph = self._page_size()
        c.saveState()
        c.translate(-ax, -ay)
        # full-bleed wash
        c.setFillColor(HexColor("#FAFBFC"))
        c.rect(0, 0, pw, ph, stroke=0, fill=1)
        c.setFillColor(self.accent)
        c.rect(0, ph - 16, pw, 16, stroke=0, fill=1)
        c.setFillColor(HexColor("#E7ECF1"))
        c.rect(0, 0, pw, 8, stroke=0, fill=1)
        c.restoreState()

        c.saveState()
        c.translate(-ax, -ay)
        y = ph - 150
        c.setFillColor(self.accent)
        c.setFont("BookSans-Bold", 9.5)
        c.drawString(ax, y, ("CHAPTER %s" % self.number).upper())
        y -= 17
        c.setStrokeColor(self.accent)
        c.setLineWidth(2.4)
        c.line(ax, y, ax + 96, y)
        y -= 38
        c.setFillColor(DEEP)
        c.setFont("BookSerif-Bold", 22)
        for ln in wrap_text(c, self.title, "BookSerif-Bold", 22, pw - 2 * OUTER):
            c.drawString(ax, y, ln)
            y -= 26
        if self.subtitle:
            y -= 8
            c.setFillColor(SLATE)
            c.setFont("BookSans", 10.0)
            for ln in wrap_text(c, self.subtitle, "BookSans", 10.0,
                                pw - 2 * OUTER):
                c.drawString(ax, y, ln)
                y -= 13.2
        # illustration
        if self.image and os.path.exists(self.image):
            iw, ih = _img_size(self.image)
            box_w = pw - 2 * OUTER
            box_h = ih * (box_w / iw)
            max_h = ph * 0.34
            if box_h > max_h:
                box_h = max_h
                box_w = iw * (box_h / ih)
            c.drawImage(self.image, ax + (pw - 2 * OUTER - box_w) / 2.0,
                        y - 14 - box_h, width=box_w, height=box_h, mask="auto")
        if self.part_label:
            c.setFillColor(MUTED)
            c.setFont("BookSans-Bold", 8.0)
            c.drawString(ax, 46, self.part_label.upper())
        c.restoreState()


class PartDivider(Flowable, FullBleedMixin):
    """Full-bleed part divider."""

    def __init__(self, number, title, blurb, image, color, chapter_list):
        Flowable.__init__(self)
        self.number = number
        self.title = title
        self.blurb = blurb
        self.image = image
        self.color = color
        self.chapter_list = chapter_list
        self.width = 0
        self.height = 0

    def wrap(self, aw, ah):
        self.width = aw
        self.height = ah
        return (aw, ah)

    def draw(self):
        c = self.canv
        ax, ay = self._page_origin()
        pw, ph = self._page_size()
        c.saveState()
        c.translate(-ax, -ay)
        c.setFillColor(self.color)
        c.rect(0, 0, pw, ph, stroke=0, fill=1)
        if self.image and os.path.exists(self.image):
            try:
                c.setFillAlpha(0.14)
            except Exception:
                pass
            iw, ih = _img_size(self.image)
            scale = max(pw / iw, ph / ih)
            c.drawImage(self.image, (pw - iw * scale) / 2.0,
                        (ph - ih * scale) / 2.0, width=iw * scale,
                        height=ih * scale, mask="auto")
            try:
                c.setFillAlpha(1.0)
            except Exception:
                pass
        c.setFillColor(ACCENT)
        c.rect(0, ph - 12, pw, 12, stroke=0, fill=1)
        c.restoreState()

        c.saveState()
        c.translate(-ax, -ay)
        y = ph - 130
        c.setFillColor(ACCENT)
        c.setFont("BookSans-Bold", 9.5)
        c.drawString(ax, y, "PART %s" % self.number)
        y -= 21
        c.setStrokeColor(ACCENT)
        c.setLineWidth(2.4)
        c.line(ax, y, ax + 90, y)
        y -= 40
        c.setFillColor(WHITE)
        c.setFont("BookSerif-Bold", 26)
        for ln in wrap_text(c, self.title, "BookSerif-Bold", 26, pw - 2 * OUTER):
            c.drawString(ax, y, ln)
            y -= 30
        y -= 10
        c.setFillColor(HexColor("#D6E1EC"))
        c.setFont("BookSans", 9.7)
        for ln in wrap_text(c, self.blurb, "BookSans", 9.7, pw - 2 * OUTER - 40):
            c.drawString(ax, y, ln)
            y -= 12.8
        y -= 18
        c.setFillColor(ACCENT)
        c.setFont("BookSans-Bold", 8.2)
        c.drawString(ax, y, "CHAPTERS IN THIS PART")
        y -= 15
        c.setFont("BookSans", 8.7)
        for num, title in self.chapter_list:
            c.setFillColor(HexColor("#9FB6CC"))
            c.drawString(ax + 4, y, num)
            c.setFillColor(WHITE)
            c.drawString(ax + 46, y, title)
            y -= 12.6
        c.restoreState()


# ---------------------------------------------------------------------------
# Content builders
# ---------------------------------------------------------------------------

def _walk(flowable):
    """Yield a flowable and any paragraphs nested inside it."""
    yield flowable
    content = getattr(flowable, "_content", None)
    if content:
        for f in content:
            for x in _walk(f):
                yield x
    cells = getattr(flowable, "_cellValues", None)
    if cells:
        for row in cells:
            for cell in row:
                if isinstance(cell, list):
                    for f in cell:
                        for x in _walk(f):
                            yield x
                elif hasattr(cell, "getPlainText"):
                    yield cell


SPECIAL_STYLE = {
    "objectives": ("Learning Objectives", NAVY, HexColor("#EAF1F8")),
    "keyterms": ("Key Terms at a Glance", TEAL, HexColor("#E7F2F1")),
    "case": ("Case Illustration", ACCENT, HexColor("#FBF4E6")),
    "review": ("Review and Discussion Questions", PLUM, HexColor("#F3ECF6")),
    "practice": ("Practice and Application", CRIMSON, HexColor("#F9ECEC")),
    "ethics": ("Ethical Considerations", HexColor("#2E5E8C"), HexColor("#EAF1F8")),
    "summary": ("Chapter Summary", DEEP, HexColor("#EDEFF2")),
    "glossary": ("Glossary", HexColor("#4A5568"), HexColor("#F2F4F6")),
    "callout": ("", NAVY, TINT),
    "theory": ("Theory in Brief", HexColor("#8C5A2B"), CREAM),
    "supervision": ("Supervision and Consultation", HexColor("#1B5E20"),
                    HexColor("#EAF3EA")),
}


def build_figure(path, caption, fig_no):
    if not os.path.exists(path):
        return [Paragraph("[Figure placeholder &mdash; %s]" % _mi(caption),
                           ST["figcap"])]
    iw, ih = _img_size(path)
    w = TEXT_W
    h = ih * (w / iw)
    max_h = 4.6 * inch
    if h > max_h:
        h = max_h
        w = iw * (h / ih)
    img = Image(path, width=w, height=h)
    img.hAlign = "CENTER"
    cap = Paragraph("<b>Figure %s</b> &nbsp;%s" % (fig_no, _mi(caption)),
                    ST["figcap"])
    return [KeepTogether([img, Spacer(1, 1), cap])]


def build_table(data, tbl_no=None, caption=None):
    header, rows = data["header"], data["rows"]
    ncols = len(header)

    def mk(cells, style):
        out = []
        for c in cells:
            out.append(Paragraph(_mi(c) if c else "", ST[style]))
        while len(out) < ncols:
            out.append(Paragraph("", ST[style]))
        return out

    head = mk(header, "tbl_head")
    body = [mk(r, "tbl_cell") for r in rows]

    weights = []
    for i in range(ncols):
        m = len(header[i]) * 1.30
        for r in rows:
            if i < len(r):
                m = max(m, len(r[i]) * 0.70)
        weights.append(max(6.0, min(m, 66.0)))
    total = float(sum(weights))
    widths = [TEXT_W * w / total for w in weights]

    t = Table([head] + body, colWidths=widths, repeatRows=1, hAlign="CENTER")
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, 0), 4.5),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 4.5),
        ("GRID", (0, 0), (-1, -1), 0.4, RULE),
        ("LINEBELOW", (0, 0), (-1, 0), 0.9, DEEP),
    ]
    for i in range(1, len(body) + 1):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), TINT))
        style.append(("TOPPADDING", (0, i), (-1, i), 3.4))
        style.append(("BOTTOMPADDING", (0, i), (-1, i), 3.4))
    t.setStyle(TableStyle(style))
    out = [t]
    if caption:
        out.append(Paragraph("<b>Table %s</b> &nbsp;%s"
                              % (tbl_no, _mi(caption)), ST["tblcap"]))
    else:
        out.append(Spacer(1, 7))
    return out


def _chunk_flowables(flow, max_height=430.0, width=None):
    """Split a list of flowables into groups that each fit in max_height.

    Used so that long special boxes (case illustrations, key terms,
    ethics notes) can flow across page boundaries instead of raising a
    LayoutError when the assembled table is taller than the frame.
    """
    if width is None:
        width = TEXT_W - 24
    chunks = []
    cur = []
    cur_h = 0.0
    for f in flow:
        try:
            w, h = f.wrap(width, max_height)
        except Exception:
            w, h = width, 0.0
        # A flowable that cannot fit on its own starts a fresh chunk.
        if cur and cur_h + h > max_height:
            chunks.append(cur)
            cur = []
            cur_h = 0.0
        cur.append(f)
        cur_h += h
        if cur_h >= max_height:
            chunks.append(cur)
            cur = []
            cur_h = 0.0
    if cur:
        chunks.append(cur)
    return chunks if chunks else [[]]


def _special_table(label, flow, accent, bg, cont=False):
    rows = []
    if label:
        title = label if not cont else "%s (continued)" % label
        rows.append([Paragraph(_mi(title), ST["box_title"])])
    rows.append([flow])
    t = Table(rows, colWidths=[TEXT_W], hAlign="CENTER")
    style = [
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 1), (0, 1), bg),
        ("TOPPADDING", (0, 1), (0, 1), 7),
        ("BOTTOMPADDING", (0, 1), (0, 1), 8),
        ("LEFTPADDING", (0, 1), (0, 1), 9),
        ("RIGHTPADDING", (0, 1), (0, 1), 9),
        ("LINEBEFORE", (0, 1), (0, 1), 2.6, accent),
    ]
    if label:
        style += [("BACKGROUND", (0, 0), (0, 0), accent),
                  ("TOPPADDING", (0, 0), (0, 0), 5),
                  ("BOTTOMPADDING", (0, 0), (0, 0), 5),
                  ("LEFTPADDING", (0, 0), (0, 0), 8),
                  ("RIGHTPADDING", (0, 0), (0, 0), 8)]
    t.setStyle(TableStyle(style))
    return t


# Height available to a special box on a body page.
_BOX_AVAIL = PAGE_H - TOP - BOT - 34


def _is_heading(f):
    st = getattr(f, "style", None)
    return st is not None and getattr(st, "name", "") in ("box_h4", "h4")


def _fits(label, flow, accent, bg, avail):
    if not flow:
        return True
    t = _special_table(label, flow, accent, bg)
    try:
        _w, h = t.wrap(TEXT_W, avail)
    except Exception:
        return False
    return h <= avail


def _split_to_fit(label, flow, accent, bg, avail):
    """Split a list of flowables into groups, each of which yields a
    table that fits within ``avail`` points of height.

    A greedy prefix is located by binary search on the (monotonic)
    measured table height, and a heading is never left stranded at the
    foot of a page.
    """
    if not flow:
        return [[]]
    if _fits(label, flow, accent, bg, avail):
        return [flow]
    if len(flow) == 1:
        # A single flowable that will not fit; let ReportLab deal with it.
        return [flow]

    lo, hi = 1, len(flow) - 1
    best = 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if _fits(label, flow[:mid], accent, bg, avail):
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    # Do not strand a heading at the end of a chunk: it belongs with
    # the paragraph that follows it.
    while best > 1 and _is_heading(flow[best - 1]):
        best -= 1
    out = _split_to_fit(label, flow[:best], accent, bg, avail)
    out.extend(_split_to_fit(label, flow[best:], accent, bg, avail))
    return out


def build_special(btype, btitle, body_text):
    label, accent, bg = SPECIAL_STYLE.get(btype, SPECIAL_STYLE["callout"])
    if btitle:
        label = btitle
    inner = mdparse.parse_markdown(body_text)
    flow = []
    for b in inner:
        flow.extend(_render_blocks([b], None, None, None, "box"))

    chunks = _chunk_flowables(flow)
    groups = []
    for c in chunks:
        groups.extend(_split_to_fit(label, c, accent, bg, _BOX_AVAIL))

    if len(groups) <= 1:
        t = _special_table(label, flow, accent, bg)
        return [Spacer(1, 5), t, Spacer(1, 9)]

    out = []
    for i, chunk in enumerate(groups):
        if i:
            out.append(PageBreak())
        t = _special_table(label, chunk, accent, bg, cont=(i > 0))
        out.append(Spacer(1, 5))
        out.append(t)
    out.append(Spacer(1, 9))
    return out


def _render_list(b, ctx):
    out = []
    ordered = b.meta.get("ordered")
    counters = {}
    for indent, text, is_num in b.payload:
        if indent >= 2:
            style = ST["number2"] if ordered else ST["bullet2"]
        else:
            style = ST["number"] if ordered else ST["bullet"]
        if ordered:
            counters[indent] = counters.get(indent, 0) + 1
            bullet = "%d." % counters[indent]
        else:
            bullet = "\u2022"
        out.append(Paragraph(_mi(text), style, bulletText=bullet))
    out.append(Spacer(1, 4))
    return out


def _render_blocks(blocks, figs, tbls, chap_no, ctx=None):
    out = []
    box = (ctx == "box")
    for b in blocks:
        k = b.kind
        if k == "p":
            out.append(Paragraph(_mi(b.payload), ST["box_body"] if box
                                 else ST["body"]))
            out.append(Spacer(1, 3.8 if not box else 2.6))
        elif k == "h":
            if box:
                if b.level == 2:
                    out.append(Paragraph(_mi(b.payload), ST["box_h4"]))
                else:
                    out.append(Paragraph(_mi(b.payload), ST["box_h4"]))
            else:
                lvl = b.level
                if lvl == 2:
                    out.append(Paragraph(_mi(b.payload), ST["h2"]))
                elif lvl == 3:
                    out.append(Paragraph(_mi(b.payload), ST["h3"]))
                elif lvl == 4:
                    out.append(Paragraph(_mi(b.payload), ST["h4"]))
                else:
                    out.append(Paragraph(_mi(b.payload), ST["h5"]))
        elif k == "quote":
            out.append(Paragraph("<i>%s</i>" % _mi(b.payload), ST["quote"]))
            out.append(Spacer(1, 2))
        elif k == "list":
            out.extend(_render_list(b, ctx))
        elif k == "table":
            if tbls is not None:
                tbls[0] += 1
                tno = "%s.%d" % (chap_no, tbls[0])
                out.extend(build_table(b.payload, tno))
            else:
                out.extend(build_table(b.payload))
        elif k == "figure":
            if figs is not None:
                figs[0] += 1
                fno = "%s.%d" % (chap_no, figs[0])
            else:
                fno = "1"
            path = b.payload
            if not os.path.isabs(path):
                path = os.path.join(FIGDIR, path)
            out.extend(build_figure(path, b.meta.get("caption", ""), fno))
        elif k == "special":
            out.extend(build_special(b.payload, b.meta.get("title", ""),
                                     b.meta.get("body", "")))
        elif k == "hr":
            out.append(Spacer(1, 6))
            out.append(Rule(TEXT_W, 0.7, RULE, 4))
            out.append(Spacer(1, 4))
        elif k == "pagebreak":
            out.append(PageBreak())
        elif k == "wordcount":
            out.append(Paragraph("[[WORDCOUNT]]", ST["body"]))
    return out


class BookIndex(SimpleIndex):
    """SimpleIndex with a safe placeholder for the first build pass."""

    def _getlastEntries(self, dummy=None):
        lE = self._lastEntries or self._entries
        if not lE:
            return [(("Index",), [((0, 0), None)])]
        return list(sorted(lE.items()))


# ---------------------------------------------------------------------------
# Page template with mirrored margins
# ---------------------------------------------------------------------------

class BodyTemplate(PageTemplate):
    def beforeDrawPage(self, canv, doc):
        f = self.frames[0]
        if getattr(doc, "page", 0) % 2 == 1:
            f._leftPadding = GUTTER
            f._rightPadding = 0
        else:
            f._leftPadding = 0
            f._rightPadding = GUTTER


# ---------------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------------

class BookDoc(BaseDocTemplate):
    def __init__(self, filename, **kw):
        BaseDocTemplate.__init__(self, filename, pagesize=(PAGE_W, PAGE_H),
                                 leftMargin=OUTER, rightMargin=OUTER,
                                 topMargin=TOP, bottomMargin=BOT,
                                 title="CAC. 701 Fundamentals of Counseling "
                                       "Theories",
                                 author="Triune Biblical University Global "
                                        "Extension",
                                 subject="Master of Arts in Children and "
                                         "Adolescent Counseling - CAC. 701",
                                 creator="Triune Biblical University Global "
                                         "Extension",
                                 keywords="counseling theory, children, "
                                          "adolescents, graduate counseling",
                                 **kw)
        self._front_offset = None
        self._section = "front"
        self._chapter_label = ""
        self._in_body = False
        self._bookmark_id = 0

        cover = Frame(0, 0, PAGE_W, PAGE_H, id="cover", leftPadding=0,
                      bottomPadding=0, rightPadding=0, topPadding=0)
        front = Frame(OUTER, BOT, PAGE_W - 2 * OUTER, PAGE_H - TOP - BOT,
                      id="front", leftPadding=0, bottomPadding=0,
                      rightPadding=0, topPadding=0)
        body = Frame(OUTER, BOT, PAGE_W - 2 * OUTER, PAGE_H - TOP - BOT,
                     id="body", leftPadding=GUTTER, bottomPadding=0,
                     rightPadding=0, topPadding=0)
        plate = Frame(OUTER, BOT, PAGE_W - 2 * OUTER, PAGE_H - TOP - BOT,
                      id="plate", leftPadding=GUTTER, bottomPadding=0,
                      rightPadding=0, topPadding=0)
        self.addPageTemplates([
            PageTemplate(id="cover", frames=[cover], onPage=self._cover_page),
            PageTemplate(id="front", frames=[front], onPage=self._front_page),
            BodyTemplate(id="body", frames=[body], onPage=self._body_page),
            BodyTemplate(id="plate", frames=[plate], onPage=self._plate_page),
        ])

    # -- furniture ---------------------------------------------------------
    def _cover_page(self, canv, doc):
        canv.saveState()
        img = os.path.join(FIGDIR, "cover.png")
        if os.path.exists(img):
            iw, ih = _img_size(img)
            scale = max(PAGE_W / iw, PAGE_H / ih)
            w, h = iw * scale, ih * scale
            canv.drawImage(img, (PAGE_W - w) / 2.0, (PAGE_H - h) / 2.0,
                           width=w, height=h, mask="auto")
        canv.setFillColor(NAVY)
        canv.rect(0, PAGE_H - 4.10 * inch, PAGE_W, 4.10 * inch, stroke=0, fill=1)
        canv.setFillColor(ACCENT)
        canv.rect(0, PAGE_H - 4.17 * inch, PAGE_W, 0.07 * inch, stroke=0, fill=1)
        canv.setFillColor(WHITE)
        canv.setFont("BookSans-Bold", 10.2)
        canv.drawString(OUTER, PAGE_H - 0.92 * inch,
                        "TRIUNE BIBLICAL UNIVERSITY GLOBAL EXTENSION")
        canv.setFont("BookSans", 8.4)
        canv.setFillColor(HexColor("#B9CBDB"))
        canv.drawString(OUTER, PAGE_H - 1.13 * inch,
                        "Global Extension  |  United States of America")
        canv.setStrokeColor(ACCENT)
        canv.setLineWidth(2.0)
        canv.line(OUTER, PAGE_H - 1.38 * inch, OUTER + 1.1 * inch,
                 PAGE_H - 1.38 * inch)
        canv.setFillColor(WHITE)
        canv.setFont("BookSerif-Bold", 30)
        y = PAGE_H - 1.92 * inch
        for ln in wrap_text(canv, "Fundamentals of", "BookSerif-Bold", 30,
                            PAGE_W - 2 * OUTER):
            canv.drawString(OUTER, y, ln)
            y -= 33
        for ln in wrap_text(canv, "Counseling Theories", "BookSerif-Bold", 30,
                            PAGE_W - 2 * OUTER):
            canv.drawString(OUTER, y, ln)
            y -= 33
        canv.setFont("BookSans-Bold", 12.0)
        canv.setFillColor(HexColor("#E3ECF4"))
        canv.drawString(OUTER, y - 4, "CAC. 701")
        canv.setFont("BookSerif-Italic", 11.0)
        canv.setFillColor(WHITE)
        canv.drawString(OUTER, y - 28, "A Graduate Textbook for the Master of "
                                      "Arts in")
        canv.drawString(OUTER, y - 44, "Children and Adolescent Counseling")
        canv.setStrokeColor(HexColor("#41608A"))
        canv.setLineWidth(0.7)
        canv.line(OUTER, 1.60 * inch, PAGE_W - OUTER, 1.60 * inch)
        canv.setFont("BookSans", 9.0)
        canv.setFillColor(HexColor("#B9CBDB"))
        canv.drawString(OUTER, 1.38 * inch,
                        "First Edition   |   Course Unit 1.6   |   Graduate "
                        "Level   |   Printed for the Academy")
        canv.setFillColor(NAVY)
        canv.rect(0, 0, PAGE_W, 1.12 * inch, stroke=0, fill=1)
        canv.setFillColor(WHITE)
        canv.setFont("BookSans-Bold", 8.8)
        canv.drawString(OUTER, 0.72 * inch,
                        "DEPARTMENT OF COUNSELING AND HUMAN DEVELOPMENT")
        canv.setFont("BookSans", 8.0)
        canv.setFillColor(HexColor("#B9CBDB"))
        canv.drawString(OUTER, 0.50 * inch,
                        "Master of Arts in Children and Adolescent Counseling")
        canv.restoreState()

    def _front_page(self, canv, doc):
        canv.saveState()
        pn = canv.getPageNumber()
        canv.setFont("BookSans", 8.0)
        canv.setFillColor(MUTED)
        canv.drawCentredString(PAGE_W / 2.0, BOT * 0.46, roman(pn))
        canv.restoreState()

    def _plate_page(self, canv, doc):
        """Illustration plates carry no running head or folio."""
        canv.saveState()
        if self._front_offset is None:
            self._front_offset = canv.getPageNumber() - 1
        canv.restoreState()

    def _body_page(self, canv, doc):
        canv.saveState()
        pn = canv.getPageNumber()
        if self._front_offset is None:
            self._front_offset = pn - 1
        label = pn - self._front_offset
        odd = (pn % 2 == 1)
        left = OUTER + (GUTTER if odd else 0)
        right = PAGE_W - (OUTER if odd else OUTER + GUTTER)
        canv.setFont("BookSans", 7.7)
        canv.setFillColor(MUTED)
        head = self._chapter_label or \
            "CAC. 701  |  Fundamentals of Counseling Theories"
        if odd:
            canv.drawRightString(right, PAGE_H - TOP + 22, head)
        else:
            canv.drawString(left, PAGE_H - TOP + 22,
                            "CAC. 701  |  Fundamentals of Counseling Theories")
        canv.setStrokeColor(RULE)
        canv.setLineWidth(0.5)
        y = PAGE_H - TOP + 15
        canv.line(left, y, right, y)
        canv.setFont("BookSans-Bold", 9.0)
        canv.setFillColor(DEEP)
        if odd:
            canv.drawRightString(right, BOT * 0.44, str(label))
        else:
            canv.drawString(left, BOT * 0.44, str(label))
        canv.restoreState()

    # -- notifications -----------------------------------------------------
    def afterFlowable(self, flowable):
        for f in _walk(flowable):
            self._after_one(f)

    def _after_one(self, flowable):
        if not isinstance(flowable, Paragraph):
            return
        style = flowable.style.name
        text = flowable.getPlainText()
        page = self.page
        disp = page - (self._front_offset or 0)
        if style == "h2":
            self.notify("TOCEntry", (2, text, disp))
        elif style == "h3":
            self.notify("TOCEntry", (3, text, disp))
        elif style == "figcap":
            self.notify("FigureEntry", (0, text, disp))
        elif style == "tblcap":
            self.notify("TableEntry", (0, text, disp))
        if self._in_body and INDEX_RE is not None and style in (
                "body", "lead", "bullet", "number", "box_body", "box_bullet",
                "box_number", "quote", "small"):
            self._scan_index(text, disp)

    def _scan_index(self, text, disp):
        for m in INDEX_RE.finditer(text):
            label = INDEX_MAP.get(m.lastgroup)
            if label:
                self.notify("IndexEntry", ((label,), disp))

    def add_bookmark(self, text, level=0):
        self._bookmark_id += 1
        key = "bm%d" % self._bookmark_id
        try:
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(text[:96], key, level=level, closed=False)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------

def read_blocks(path):
    with open(path, "r", encoding="utf-8") as fh:
        return mdparse.parse_markdown(fh.read())


def _render_front_blocks(blocks):
    out = []
    for b in blocks:
        if b.kind == "h":
            if b.level == 1:
                out.append(Paragraph(_mi(b.payload), ST["fm_title"]))
                out.append(Rule(TEXT_W, 1.2, ACCENT, 6))
                out.append(Spacer(1, 8))
            elif b.level == 2:
                out.append(Paragraph(_mi(b.payload), ST["fm_h2"]))
            elif b.level == 3:
                out.append(Paragraph(_mi(b.payload), ST["fm_h3"]))
        elif b.kind == "p":
            out.append(Paragraph(_mi(b.payload), ST["body"]))
            out.append(Spacer(1, 4.2))
        elif b.kind == "list":
            out.extend(_render_list(b, None))
        elif b.kind == "table":
            out.extend(build_table(b.payload))
        elif b.kind == "figure":
            path = b.payload
            if not os.path.isabs(path):
                path = os.path.join(FIGDIR, path)
            out.extend(build_figure(path, b.meta.get("caption", ""), "1"))
        elif b.kind == "special":
            out.extend(build_special(b.payload, b.meta.get("title", ""),
                                     b.meta.get("body", "")))
        elif b.kind == "quote":
            out.append(Paragraph("<i>%s</i>" % _mi(b.payload), ST["quote"]))
            out.append(Spacer(1, 2))
        elif b.kind == "hr":
            out.append(Rule(TEXT_W, 0.7, RULE, 5))
        elif b.kind == "pagebreak":
            out.append(PageBreak())
        elif b.kind == "wordcount":
            out.append(Paragraph("[[WORDCOUNT]]", ST["body"]))
    return out


def count_words():
    total = 0
    for root, _dirs, files in os.walk(CONTENT):
        for f in files:
            if not f.endswith(".md"):
                continue
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8") as fh:
                total += mdparse.count_words_in_blocks(
                    mdparse.parse_markdown(fh.read()))
    return total


def main():
    global WORD_TOTAL
    load_index_terms(os.path.join(CONTENT, "index_terms.json"))
    with open(os.path.join(CONTENT, "manifest.json"), "r",
              encoding="utf-8") as fh:
        manifest = json.load(fh)

    WORD_TOTAL = count_words()
    print("Manuscript word count: %s" % format(WORD_TOTAL, ","))

    if not os.path.isdir(DIST):
        os.makedirs(DIST)
    out_path = os.path.join(
        DIST, "CAC-701-Fundamentals-of-Counseling-Theories.pdf")

    doc = BookDoc(out_path)
    story = []

    def pb():
        """Append a page break, collapsing consecutive breaks."""
        last = None
        for f in reversed(story):
            if isinstance(f, NextPageTemplate):
                continue
            last = f
            break
        if isinstance(last, PageBreak):
            return
        story.append(PageBreak())

    # cover
    story.append(NextPageTemplate("front"))
    story.append(Spacer(1, 1))
    story.append(PageBreak())

    # front matter
    front_dir = os.path.join(CONTENT, "front")
    for name in manifest.get("front_order", []):
        path = os.path.join(front_dir, name)
        if not os.path.exists(path):
            print("  !! missing front file: %s" % name)
            continue
        story.extend(_render_front_blocks(read_blocks(path)))

    # table of contents
    pb()
    story.append(Paragraph("Table of Contents", ST["fm_title"]))
    story.append(Rule(TEXT_W, 1.2, ACCENT, 6))
    story.append(Spacer(1, 10))
    toc = TableOfContents()
    toc.levelStyles = [ST["toc1"], ST["toc2"], ST["toc3"], ST["toc4"]]
    toc.dotsMinLevel = 1
    story.append(toc)

    # list of figures
    pb()
    story.append(Paragraph("List of Figures", ST["fm_title"]))
    story.append(Rule(TEXT_W, 1.2, ACCENT, 6))
    story.append(Spacer(1, 10))
    lof = TableOfContents(notifyKind="FigureEntry")
    lof.levelStyles = [ST["toc2"]]
    lof.dotsMinLevel = 0
    story.append(lof)

    # list of tables
    pb()
    story.append(Paragraph("List of Tables", ST["fm_title"]))
    story.append(Rule(TEXT_W, 1.2, ACCENT, 6))
    story.append(Spacer(1, 10))
    lot = TableOfContents(notifyKind="TableEntry")
    lot.levelStyles = [ST["toc2"]]
    lot.dotsMinLevel = 0
    story.append(lot)

    # body
    doc._in_body = True
    figs = [0]
    tbls = [0]
    for part in manifest["parts"]:
        pcolor = HexColor(part.get("accent", "#173A5E"))
        chapters = part["chapters"]
        opener = _resolve(part.get("opener", ""))
        story.append(NextPageTemplate("plate"))
        pb()
        story.append(PartDivider(part["number"], part["title"],
                                 part.get("blurb", ""), opener,
                                 pcolor,
                                 [(c["number"], c["title"]) for c in chapters]))
        story.append(NextPageTemplate("body"))
        pb()
        doc.add_bookmark("Part %s: %s" % (part["number"], part["title"]), 0)
        for ch in chapters:
            ch_files = ch.get("files") or ([ch["file"]] if "file" in ch else [])
            missing = [f for f in ch_files
                       if not os.path.exists(os.path.join(CONTENT, f))]
            if missing:
                for f in missing:
                    print("  !! missing: %s" % f)
                if len(missing) == len(ch_files):
                    continue
            doc._chapter_label = "Chapter %s  |  %s" % (ch["number"],
                                                       ch["title"])
            story.append(NextPageTemplate("plate"))
            pb()
            story.append(ChapterOpener(
                ch["number"], ch["title"], ch.get("subtitle", ""),
                _resolve(ch.get("opener", "")),
                part["title"], pcolor))
            story.append(NextPageTemplate("body"))
            pb()
            doc.add_bookmark("Chapter %s: %s" % (ch["number"], ch["title"]), 0)
            for f in ch_files:
                path = os.path.join(CONTENT, f)
                if not os.path.exists(path):
                    continue
                blocks = read_blocks(path)
                for b in blocks:
                    if b.kind == "h" and b.level == 1:
                        continue
                    story.extend(_render_blocks([b], figs, tbls, ch["number"]))

    # appendices
    for ap in manifest.get("appendices", []):
        ap_files = ap.get("files") or ([ap["file"]] if "file" in ap else [])
        missing = [f for f in ap_files
                   if not os.path.exists(os.path.join(CONTENT, f))]
        if missing:
            for f in missing:
                print("  !! missing: %s" % f)
            if len(missing) == len(ap_files):
                continue
        doc._chapter_label = "Appendix %s  |  %s" % (ap["letter"], ap["title"])
        story.append(NextPageTemplate("plate"))
        pb()
        story.append(ChapterOpener(ap["label"], ap["title"],
                                   ap.get("subtitle", ""), None,
                                   "Appendix", HexColor("#2E5E8C")))
        story.append(NextPageTemplate("body"))
        pb()
        doc.add_bookmark("Appendix %s: %s" % (ap["letter"], ap["title"]), 0)
        for f in ap_files:
            path = os.path.join(CONTENT, f)
            if not os.path.exists(path):
                continue
            blocks = read_blocks(path)
            for b in blocks:
                if b.kind == "h" and b.level == 1:
                    continue
                story.extend(_render_blocks([b], figs, tbls, ap["label"]))

    # index
    pb()
    story.append(Paragraph("Index", ST["fm_title"]))
    story.append(Rule(TEXT_W, 1.2, ACCENT, 6))
    story.append(Spacer(1, 10))
    idx = BookIndex(style=[ST["index_a"], ST["index"]], dot=" . ",
                    headers=True, name="mainindex")
    story.append(idx)

    # substitute word count placeholder
    story = _substitute_wordcount(story)

    doc.multiBuild(story)
    print("PDF written to %s" % out_path)


def _resolve(rel):
    if not rel:
        return None
    p = os.path.join(FIGDIR, rel)
    return p if os.path.exists(p) else None


def _substitute_wordcount(story):
    txt = format(WORD_TOTAL, ",")
    out = []
    for f in story:
        if isinstance(f, Paragraph) and "[[WORDCOUNT]]" in f.text:
            f = Paragraph(f.text.replace("[[WORDCOUNT]]", txt), f.style)
        out.append(f)
    return out


if __name__ == "__main__":
    main()
