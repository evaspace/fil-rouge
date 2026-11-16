import re
import unittest

from filrouge import SrcU, draw, echelle, save


class FilRougeTest(unittest.TestCase):
    def test_voltage_source_has_crossing_wire(self):
        svg = draw(lambda d: d.add(SrcU().endpoints((0, 0), (0, 3))))
        self.assertEqual(svg.count("<circle"), 1)
        self.assertEqual(len(re.findall(r"<path d=", svg)), 2)  # leads + the wire crossing the circle

    def test_math_labels_are_outlines(self):
        svg = draw(lambda d: echelle(d, "E", [("s", "R", "R_1"), ("p", "C", "C")], "u_C"))
        self.assertNotIn("<text", svg)  # ziamath turned the labels into paths

    def test_reversed_diode_swaps_ends(self):
        def anode_at_top(code):
            svg = draw(lambda d: echelle(d, "E", [("s", "R", "R"), ("p", code, "D")]))
            return svg
        self.assertNotEqual(anode_at_top("D"), anode_at_top("D<"))

    def test_save_is_stable(self):
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            fn = lambda d: echelle(d, "E", [("s", "R", "R"), ("p", "C", "C")], "u")  # noqa: E731
            self.assertEqual(save(fn, t), save(fn, t))


if __name__ == "__main__":
    unittest.main()
