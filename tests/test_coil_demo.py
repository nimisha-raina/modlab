"""Check the coil's field direction, pole reversal and disconnected cell swap."""

import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from electromagnetism import coil_demo as demo, current_demo
from electromagnetism.camera_path import OPENING_WIDE, opening_pose, camera_pose
from electromagnetism.config import LESSON


class CoilTests(unittest.TestCase):
    def test_six_turns_and_fixed_connections(self):
        straight, wound = demo.wire_points(0), demo.wire_points(1)
        self.assertEqual(straight[0], wound[0])
        self.assertLess(math.dist(straight[-1], wound[-1]), 1e-12)
        angles = [math.atan2(p[2]-demo.CENTER[2], p[1]-demo.CENTER[1]) for p in wound[36:325]]
        total = sum((b-a+math.pi) % (2*math.pi)-math.pi for a, b in zip(angles, angles[1:]))
        self.assertAlmostEqual(total/(2*math.pi), 6)
        self.assertGreater(demo.LENGTH/demo.TURNS, 2*.085)

    def test_current_reversal_reverses_field(self):
        field = demo.field_at(demo.CENTER)
        reverse = demo.field_at(demo.CENTER, current=-1)
        self.assertLess(field[0], 0)  # Left N, right S for conventional current.
        for a, b in zip(field, reverse):
            self.assertAlmostEqual(a, -b)
        self.assertAlmostEqual(demo.current_at(16), 1)
        self.assertEqual(demo.current_at(23.5), 0)
        self.assertEqual(demo.current_at(26), -1)

    def test_needle_returns_to_earth_field_while_disconnected(self):
        north = demo.NORTH_ANGLE
        self.assertAlmostEqual(demo.compass_angle(1, 0), north)
        forward, reverse = [demo.compass_angle(1, i) for i in (1, -1)]
        self.assertAlmostEqual(forward-north, -(reverse-north))
        self.assertAlmostEqual(abs(forward-north), math.radians(35))

    def test_board_opens_first_and_existing_micro_camera_is_retained(self):
        for t in (0, 1):
            for a, b in zip(opening_pose(t), OPENING_WIDE):
                self.assertLess(math.dist(a, b), 1e-12)
        self.assertEqual(opening_pose(LESSON.microscope_in), camera_pose(LESSON.microscope_in))
        for a, b in zip(opening_pose(42), current_demo.camera_pose(0)):
            self.assertLess(math.dist(a, b), 1e-12)

    def test_axis_extension_is_finite_but_wire_itself_is_singular(self):
        self.assertEqual(current_demo.segment_field((2, 0, 0), (0, 0, 0), (1, 0, 0)), (0, 0, 0))
        with self.assertRaises(ValueError):
            current_demo.segment_field((.5, 0, 0), (0, 0, 0), (1, 0, 0))
