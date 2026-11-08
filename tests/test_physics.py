import math, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from physics import Params, solve, validate_inputs, energy_table, kinematics_table


class Reference(unittest.TestCase):
    def setUp(self):
        self.r, self.e = solve(Params())

    def test_no_errors(self):
        self.assertEqual(self.e, [])

    def test_velocities(self):
        self.assertAlmostEqual(self.r.point("A").v, 0.0)
        self.assertAlmostEqual(self.r.v_b, 7.67, places=2)
        self.assertAlmostEqual(self.r.v_c, 4.50, places=2)
        self.assertAlmostEqual(self.r.point("D").v, 0.0)

    def test_mu(self):
        self.assertAlmostEqual(self.r.mu, 0.328, places=3)

    def test_energies(self):
        r = self.r
        self.assertAlmostEqual(r.point("A").emec, 294.0)
        self.assertAlmostEqual(r.point("B").emec, 294.0)
        self.assertAlmostEqual(r.point("C").ek, 101.25)
        self.assertAlmostEqual(r.point("D").epel, 101.25)
        self.assertAlmostEqual(r.e_diss, 192.75)

    def test_consistency_checks(self):
        self.assertTrue(all(self.r.checks().values()))

    def test_tables(self):
        self.assertEqual(list(energy_table(self.r)["Punto"]), list("ABCD"))
        self.assertEqual(kinematics_table(self.r).shape, (4, 4))


class Validation(unittest.TestCase):
    def test_invalid_inputs(self):
        for kw in ({"m": 0}, {"h": -1}, {"d": 0}, {"k": 0}, {"x": -0.1}):
            self.assertTrue(validate_inputs(Params(**kw)), kw)
            self.assertIsNone(solve(Params(**kw))[0])

    def test_non_finite(self):
        for v in (float("nan"), float("inf")):
            self.assertIsNone(solve(Params(m=v))[0])

    def test_negative_mu(self):
        r, e = solve(Params(h=0.5, x=0.5))
        self.assertIsNone(r)
        self.assertIn("negativo", e[0])

    def test_zero_height_zero_compression(self):
        r, e = solve(Params(h=0, x=0))
        self.assertEqual(e, [])
        self.assertEqual((r.v_b, r.v_c, r.mu, r.e_diss), (0, 0, 0, 0))

    def test_zero_compression_stops_at_C(self):
        r, _ = solve(Params(x=0))
        self.assertEqual(r.v_c, 0)
        self.assertAlmostEqual(r.mu, 3 / 6)

    def test_friction_free_case(self):
        r, _ = solve(Params(h=3, x=math.sqrt(2 * 10 * 9.8 * 3 / 2250)))
        self.assertAlmostEqual(r.mu, 0.0, places=9)
        self.assertAlmostEqual(r.e_diss, 0.0, places=6)

    def test_all_finite(self):
        r, _ = solve(Params(m=0.001, h=100, d=0.01, k=1.0, x=0.1))
        for s in r.points:
            for v in (s.v, s.y, s.c, s.ek, s.epy, s.epel):
                self.assertTrue(math.isfinite(v))


if __name__ == "__main__":
    unittest.main(verbosity=2)
