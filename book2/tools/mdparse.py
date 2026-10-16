"""
Lightweight, dependency-free Markdown parser tuned for the CAC. 701 textbook.

Supported block constructs
--------------------------
#            chapter / appendix title (level 1)
##           section heading (level 2)
###          subsection heading (level 3)
####         sub-subsection heading (level 4)
#####        minor heading (level 5)
plain text   paragraph
- / *        bullet list (two-space nesting allowed)
1.           ordered list
>            block quotation
| a | b |    pipe table (header row + separator row + body)
:::type      opens a styled block; ::: closes it
![cap](path)figure with auto-numbering and caption
---          thematic break
[[PAGEBREAK]] forced page break
[[WORDCOUNT]] replaced at render time with the book word count

Supported inline constructs
---------------------------
**bold**  *italic*  _italic_  `code`  ^^small caps^^  ~sub~  ==highlight==
"""

import re
import os

# --------------------------------------------------------------------------
# Inline handling
# --------------------------------------------------------------------------

_TOKEN_RE = re.compile(
    r"(\*\*.+?\*\*"
    r"|(?<!\*)\*(?!\*).+?(?<!\*)\*(?!\*)"
    r"|(?<![\w_])_(?!\s)[^_]+?_(?!\w)"
    r"|`[^`]+`"
    r"|\^\^.+?\^\^"
    r"|~[^~]+~"
    r"|==.+?=="
    r"|\[[^\]]+\]\([^)]+\))"
)


def _escape(text):
    """Escape XML-significant characters for ReportLab Paragraph markup."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _inline(text):
    """Convert a line of markdown into ReportLab-safe inline markup."""
    out = []
    pos = 0
    for m in _TOKEN_RE.finditer(text):
        out.append(_escape(text[pos:m.start()]))
        tok = m.group(0)
        if tok.startswith("**"):
            out.append("<b>%s</b>" % _escape(tok[2:-2]))
        elif tok.startswith("`"):
            out.append('<font face="Courier" size="8.6">%s</font>' % _escape(tok[1:-1]))
        elif tok.startswith("^^"):
            out.append('<font face="DejaVuSans" size="7.6" color="#4A5568">%s</font>'
                       % _escape(tok[2:-2]).upper())
        elif tok.startswith("=="):
            out.append('<font backColor="#FFF3C4">%s</font>' % _escape(tok[2:-2]))
        elif tok.startswith("~"):
            out.append("<sub>%s</sub>" % _escape(tok[1:-1]))
        elif tok.startswith("["):
            label, url = tok[1:-1].split("(", 1)
            out.append('<link href="%s" color="#1F4E79">%s</link>'
                       % (_escape(url.rstrip(")")), _escape(label)))
        else:  # italic
            out.append("<i>%s</i>" % _escape(tok.strip("*_")))
        pos = m.end()
    out.append(_escape(text[pos:]))
    return "".join(out)


# --------------------------------------------------------------------------
# Block parsing
# --------------------------------------------------------------------------

BULLET_RE = re.compile(r"^(\s*)[-*]\s+(.*)$")
NUMBER_RE = re.compile(r"^(\s*)(\d+)[.)]\s+(.*)$")


class Block(object):
    """A single parsed block of the manuscript."""

    __slots__ = ("kind", "payload", "level", "meta")

    def __init__(self, kind, payload=None, level=0, meta=None):
        self.kind = kind
        self.payload = payload
        self.level = level
        self.meta = meta or {}

    def __repr__(self):  # pragma: no cover - debugging aid
        return "<Block %s lvl=%s>" % (self.kind, self.level)


def _split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    cells = []
    cur = ""
    esc = False
    for ch in line:
        if esc:
            cur += ch
            esc = False
            continue
        if ch == "\\":
            esc = True
            continue
        if ch == "|":
            cells.append(cur.strip())
            cur = ""
            continue
        cur += ch
    cells.append(cur.strip())
    return cells


def _is_separator(line):
    s = line.strip()
    if not s or "|" not in s:
        return False
    return all(re.match(r"^\s*:?-{2,}:?\s*$", c) for c in _split_row(s))


def parse_markdown(text):
    """Parse a markdown source string into a list of :class:`Block` objects."""
    lines = text.replace("\r\n", "\n").split("\n")
    blocks = []
    i = 0
    n = len(lines)
    para = []

    def flush_para():
        if para:
            blocks.append(Block("p", " ".join(para)))
            del para[:]

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # forced page break
        if stripped == "[[PAGEBREAK]]":
            flush_para()
            blocks.append(Block("pagebreak"))
            i += 1
            continue

        if stripped == "[[WORDCOUNT]]":
            flush_para()
            blocks.append(Block("wordcount"))
            i += 1
            continue

        # fenced styled block
        if stripped.startswith(":::"):
            flush_para()
            header = stripped[3:].strip()
            btype = "callout"
            btitle = ""
            if header:
                parts = header.split(None, 1)
                btype = parts[0].lower()
                btitle = parts[1].strip() if len(parts) > 1 else ""
            body = []
            i += 1
            while i < n and lines[i].strip() != ":::":
                body.append(lines[i])
                i += 1
            i += 1  # consume closing :::
            blocks.append(Block("special", btype, meta={"title": btitle,
                                                       "body": "\n".join(body)}))
            continue

        # heading
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            flush_para()
            level = len(m.group(1))
            blocks.append(Block("h", m.group(2).strip(), level=level))
            i += 1
            continue

        # figure
        m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", stripped)
        if m:
            flush_para()
            blocks.append(Block("figure", m.group(2), meta={"caption": m.group(1).strip()}))
            i += 1
            continue

        # horizontal rule
        if re.match(r"^-{3,}$", stripped):
            flush_para()
            blocks.append(Block("hr"))
            i += 1
            continue

        # table
        if "|" in line and i + 1 < n and _is_separator(lines[i + 1]):
            flush_para()
            header = _split_row(line)
            align = []
            for c in _split_row(lines[i + 1]):
                c = c.strip()
                if c.startswith(":") and c.endswith(":"):
                    align.append("center")
                elif c.endswith(":"):
                    align.append("right")
                else:
                    align.append("left")
            i += 2
            rows = []
            while i < n and lines[i].strip() and "|" in lines[i]:
                rows.append(_split_row(lines[i]))
                i += 1
            blocks.append(Block("table", {"header": header, "rows": rows, "align": align}))
            continue

        # blockquote
        if stripped.startswith(">"):
            flush_para()
            q = []
            while i < n and lines[i].strip().startswith(">"):
                q.append(lines[i].strip().lstrip(">").strip())
                i += 1
            blocks.append(Block("quote", " ".join(q)))
            continue

        # list
        if BULLET_RE.match(line) or NUMBER_RE.match(line):
            flush_para()
            items = []
            ordered = bool(NUMBER_RE.match(line))
            while i < n:
                cur = lines[i]
                if not cur.strip():
                    # blank line: continue only if the next line is a list
                    # item of the *same* kind
                    j = i + 1
                    if j < n:
                        nb = BULLET_RE.match(lines[j])
                        nn = NUMBER_RE.match(lines[j])
                        if (nb and not ordered) or (nn and ordered):
                            i = j
                            continue
                    break
                mb = BULLET_RE.match(cur)
                mn = NUMBER_RE.match(cur)
                if mb and not ordered:
                    indent = len(mb.group(1))
                    items.append((indent, mb.group(2).strip(), False))
                    i += 1
                    continue
                if mn and ordered:
                    indent = len(mn.group(1))
                    items.append((indent, mn.group(3).strip(), True))
                    i += 1
                    continue
                # continuation line of previous item
                if items and cur.startswith(("  ", "\t")) and cur.strip():
                    ind, txt, _ = items[-1]
                    items[-1] = (ind, txt + " " + cur.strip(), False)
                    i += 1
                    continue
                break
            blocks.append(Block("list", items, meta={"ordered": ordered}))
            continue

        # blank line
        if not stripped:
            flush_para()
            i += 1
            continue

        # ordinary paragraph line
        para.append(stripped)
        i += 1

    flush_para()
    return blocks


def read_blocks(path):
    with open(path, "r", encoding="utf-8") as fh:
        return parse_markdown(fh.read())


# --------------------------------------------------------------------------
# Word counting
# --------------------------------------------------------------------------

_WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'’\-/]*")


def count_words_in_blocks(blocks):
    total = 0

    def scan(text):
        return len(_WORD_RE.findall(text))

    for b in blocks:
        if b.kind == "p":
            total += scan(b.payload)
        elif b.kind in ("h", "quote"):
            total += scan(b.payload)
        elif b.kind == "list":
            for _ind, txt, _o in b.payload:
                total += scan(txt)
        elif b.kind == "table":
            for c in b.payload["header"]:
                total += scan(c)
            for r in b.payload["rows"]:
                for c in r:
                    total += scan(c)
        elif b.kind == "special":
            total += scan(b.meta.get("body", ""))
            total += scan(b.meta.get("title", ""))
        elif b.kind == "figure":
            total += scan(b.meta.get("caption", ""))
    return total
