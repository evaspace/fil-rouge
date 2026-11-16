"""Draw the README gallery into docs/. Run: python examples/gallery.py"""
from pathlib import Path

from filrouge import R, Fil, Point, SrcI, SrcU, courant, draw, echelle, tension

DOCS = Path(__file__).resolve().parents[1] / "docs"


def thevenin_norton(d):
    """A voltage source, a current source and four resistors: a classic Thévenin/Norton exercise."""
    d += (s := SrcU().endpoints((0, 0), (0, 4)))
    tension(d, s, "$E$")
    d += R().endpoints((0, 4), (3, 4)).label("$R_1$")
    d += R().endpoints((3, 4), (3, 0)).label("$R_2$", loc="bottom")
    d += R().endpoints((3, 4), (6, 4)).label("$R_3$")
    d += Point().at((6, 4)).label("$A$", loc="top")
    d += (r := R().endpoints((6, 4), (6, 0)).label("$R_L$", loc="top"))
    tension(d, r, "$U$", sens=-1)
    d += Point().at((6, 0)).label("$B$", loc="bottom")
    d += Fil().endpoints((6, 4), (9, 4))
    d += (s := SrcI().endpoints((9, 0), (9, 4)))
    courant(d, s, "$\\eta$", debut=False)
    d += Fil().endpoints((0, 0), (9, 0))


GALLERY = {
    "rc-low-pass": lambda d: echelle(d, "v_e(t)", [("s", "R", "R"), ("p", "C", "C")], "v_s(t)"),
    "rlc-ladder": lambda d: echelle(d, "v_e(t)", [("s", "R", "R"), ("p", "C", "C"), ("s", "L", "L"),
                                                   ("p", "R", "R")], "v_s(t)"),
    "zener-regulator": lambda d: echelle(d, "E", [("s", "R", "R"), ("p", "DZ<", "D_Z"), ("p", "R", "R_c")], "U"),
    "half-wave-rectifier": lambda d: echelle(d, "e(t)", [("s", "D", "D"), ("p", "R", "R")], "u(t)"),
    "rl-switch": lambda d: echelle(d, "E", [("s", "K", "K"), ("s", "R", "R"), ("p", "R", "R"), ("p", "L", "L")],
                                   "u_L(t)"),
    "thevenin-norton": thevenin_norton,
}

if __name__ == "__main__":
    DOCS.mkdir(exist_ok=True)
    for name, fn in GALLERY.items():
        (DOCS / f"{name}.svg").write_text(draw(fn))
        print("docs/" + name + ".svg")
