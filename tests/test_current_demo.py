"""Physical relationships and the independent chapter's motion constraints."""

import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from electromagnetism import current_demo as demo


class CurrentDemoTests(unittest.TestCase):
    def test_straight_wire_direction_and_inverse_distance(self):
        a = demo.segment_field((0, 0, -1), (1000, 0, 0), (-1000, 0, 0))
        b = demo.segment_field((0, 0, -2), (1000, 0, 0), (-1000, 0, 0))
        self.assertLess(a[1], 0)
        self.assertAlmostEqual(a[1]/b[1], 2, places=5)

    def test_current_doubles_field_and_reversal_changes_sign(self):
        for point in (demo.COMPASS_CENTER, (1, 1, .3)):
            a, b, c = [demo.circuit_field(point, i) for i in (1, 2, -1)]
            for x, y, z in zip(a, b, c):
                self.assertAlmostEqual(y, 2*x)
                self.assertAlmostEqual(z, -x)

    def test_compass_uses_total_field_and_nonlinear_angle(self):
        zero, one, two = [demo.compass_angle(i) for i in (0, 1, 2)]
        self.assertAlmostEqual(zero, demo.NORTH_ANGLE)
        self.assertAlmostEqual(math.tan(zero-two), 2*math.tan(zero-one))
        self.assertGreater(abs(two-zero), abs(one-zero))
        self.assertLess(abs(two-zero), 2*abs(one-zero))

    def test_current_cases_and_repeatable_comparison(self):
        self.assertEqual([demo.current_at(t) for t in (0, 4.9, 8, 18, 23)], [1, 1, 1, 2, 1])
        self.assertEqual(demo.camera_pose(8), demo.camera_pose(18))
        previous = demo.camera_pose(0)[0]
        for frame in range(demo.DURATION*demo.FPS):
            time = frame/demo.FPS
            position, target = demo.camera_pose(time)
            self.assertLess(math.dist(previous, position)/math.dist(position, target), .06)
            self.assertTrue(1 <= demo.current_at(time) <= 2)
            previous = position

    def test_meter_is_in_series_and_compass_settles_before_comparison(self):
        self.assertEqual(demo.CURRENT_PATH[2:2+len(demo.METER_PATH)], demo.METER_PATH)
        self.assertNotIn(((-5, -2.2, .7), (-5, 2.2, 1.6)), list(zip(demo.CURRENT_PATH, demo.CURRENT_PATH[1:])))
        self.assertEqual(demo.compass_position(8), demo.COMPASS_CENTER)
        self.assertEqual(demo.compass_position(18), demo.COMPASS_CENTER)
        self.assertGreater(math.dist(demo.compass_position(1), demo.COMPASS_CENTER), 1)
        initial_angle = demo.compass_angle(1, demo.compass_position(demo.PLACEMENT_START))
        self.assertLess(abs(initial_angle-demo.NORTH_ANGLE), math.radians(2))


if __name__ == "__main__":
    unittest.main()
