"""fil-rouge: electric circuit diagrams as SVG, drawn the way French textbooks and exams draw them.

Built on schemdraw. Labels written `$...$` are LaTeX, turned into outlines by ziamath, so the SVG looks the
same everywhere (no font needed on the reader's device).

French conventions: voltage source = circle crossed by the wire (`SrcU`), current source = circle crossed
perpendicularly (`SrcI`), resistor = IEC box, voltage = arrow beside the dipole (`tension`), current = arrow head
on the wire (`courant`).
"""
import hashlib
from pathlib import Path

import schemdraw
import schemdraw.elements as elm
from schemdraw.segments import Segment, SegmentCircle

__version__ = "0.1.0"
__all__ = ["SrcU", "SrcI", "R", "C", "L", "D", "DZ", "Fil", "Point", "Masse", "Inter", "Gap",
           "tension", "courant", "echelle", "draw", "save"]

schemdraw.use("svg")
schemdraw.svgconfig.text = "path"  # math labels as outlines: same look on every device
schemdraw.svgconfig.svg2 = False

R = elm.ResistorIEC
C = elm.Capacitor
L = elm.Inductor2
D = elm.Diode
DZ = elm.Zener
Fil = elm.Line
Point = elm.Dot
Masse = elm.Ground
Inter = elm.Switch
Gap = elm.Gap


class SrcU(elm.Element2Term):
    """Ideal voltage source, French symbol: circle crossed by the wire."""
    def __init__(self, **kw):
        super().__init__(**kw)
        self.segments.append(Segment([(0, 0), (0, 0), elm.elements.gap, (1, 0), (1, 0)]))  # leads
        self.segments.append(SegmentCircle((0.5, 0), 0.5))
        self.segments.append(Segment([(0, 0), (1, 0)]))  # the wire crossing the circle


class SrcI(elm.Element2Term):
    """Ideal current source, French symbol: circle crossed perpendicularly to the wire."""
    def __init__(self, **kw):
        super().__init__(**kw)
        self.segments.append(Segment([(0, 0), (0, 0), elm.elements.gap, (1, 0), (1, 0)]))
        self.segments.append(SegmentCircle((0.5, 0), 0.5))
        self.segments.append(Segment([(0.5, -0.5), (0.5, 0.5)]))


def tension(d, e, label, sens=1, cote=True, ofst=0.6, length=1.6):
    """Voltage arrow beside element `e`. sens=1 points along the drawing direction of `e`, cote picks the side."""
    d += elm.CurrentLabel(top=cote, ofst=ofst, length=length, reverse=sens < 0).at(e).label(label)


def courant(d, e, label, sens=1, debut=True, loc=None):
    """Current arrow head on the wire of element `e`. sens=1 = along the drawing direction; loc moves the label."""
    along = "in" if debut else "out"  # schemdraw: "in" points into the element
    d += elm.CurrentLabelInline(direction=along if sens > 0 else {"in": "out", "out": "in"}[along],
                                start=debut).at(e).label(label, loc=loc)


_DIP = {"R": R, "C": C, "L": L, "D": D, "DZ": DZ, "K": Inter, "I": SrcI, "U": SrcU, "Z": R}


def _dip(code, a, b):
    """Element `code` from a to b. A diode drawn from a to b has its anode at a; a trailing '<' swaps the ends."""
    if code.endswith("<"):  # schemdraw's reverse() is ignored once endpoints() places the element
        a, b = b, a
    return _DIP[code.rstrip("<")]().endpoints(a, b)


def echelle(d, source, branches, sortie=None, sortie_sur=None):
    """Ladder circuit ("échelle"): a voltage source on the left, then `branches` from left to right.

    Each branch is ("s", code, label) for a series element on the top rail or ("p", code, label) for a shunt
    element from the top rail to the bottom rail. Codes: R C L D DZ K (switch) I U (sources) Z (impedance box);
    a trailing "<" turns a diode or Zener the other way. Labels are LaTeX without the dollars ("2R", "v_e(t)").
    `sortie` labels the output voltage, across the last shunt (or `branches[sortie_sur]`), or across open
    terminals when the circuit ends with a series element. Without `sortie`, such a circuit is closed by a wire.
    """
    H, x, prev, last, up = 3, 0, "src", None, False
    d += (s := SrcU().endpoints((0, 0), (0, H)))
    tension(d, s, f"${source}$")
    for i, (kind, code, lab) in enumerate(branches):
        text = f"${lab}$" if lab else ""
        if kind == "s":
            d += _dip(code, (x, H), (x + 3, H)).label(text)
            d += Fil().endpoints((x, 0), (x + 3, 0))
            x += 3
        else:
            if prev != "s":  # two shunts side by side need a wire between them
                d += Fil().endpoints((x, H), (x + 2, H))
                d += Fil().endpoints((x, 0), (x + 2, 0))
                x += 2
            d += (e := _dip(code, (x, H), (x, 0)).label(text, loc="bottom"))
            if i == (len(branches) - 1 if sortie_sur is None else sortie_sur):
                last, up = e, code.endswith("<")  # `up`: drawn bottom to top
        prev = kind
    if not sortie and prev == "s":
        d += Fil().endpoints((x, H), (x, 0))
    if sortie and last is not None:
        tension(d, last, f"${sortie}$", sens=1 if up else -1, cote=not up, ofst=0.9)
    elif sortie:  # open output terminals after a series element
        d += Fil().endpoints((x, H), (x + 1.5, H))
        d += Fil().endpoints((x, 0), (x + 1.5, 0))
        d += Point(open=True).at((x + 1.5, H))
        d += Point(open=True).at((x + 1.5, 0))
        d += (g := Gap().endpoints((x + 1.5, H), (x + 1.5, 0)))
        tension(d, g, f"${sortie}$", sens=-1, ofst=0.4)


def draw(fn, fontsize=19, lw=1.6):
    """SVG text of the circuit drawn by `fn(d)` on a fresh schemdraw Drawing."""
    with schemdraw.Drawing(show=False, unit=2.5, fontsize=fontsize, lw=lw) as d:
        fn(d)
    return d.get_imagedata("svg").decode()


def save(fn, folder, prefix="circuit-", **kw):
    """Draw `fn(d)` and write it to `folder/<prefix><hash>.svg` (same drawing, same name). Returns the path."""
    svg = draw(fn, **kw)
    path = Path(folder) / f"{prefix}{hashlib.sha1(svg.encode()).hexdigest()[:12]}.svg"
    if not path.exists() or path.read_text() != svg:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(svg)
    return path
