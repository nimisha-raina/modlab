"""Check the coil's field direction, pole reversal and disconnected cell swap."""

import math
import importlib.util
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from electromagnetism import coil_demo as demo, current_demo
from electromagnetism.camera_path import OPENING_WIDE, opening_pose, camera_pose
from electromagnetism.config import LESSON
from electromagnetism.wire_winding import length


class CoilTests(unittest.TestCase):
    def test_case_two_camera_does_not_move_between_experiments(self):
        initial = demo.camera_pose(0)
        for seconds in range(demo.DURATION+1):
            self.assertEqual(demo.camera_pose(seconds),initial)

    def test_clips_attach_beyond_the_winding(self):
        for index in range(6):
            x,y = demo.clip_site(index)
            self.assertGreater(abs(x)-.11,demo.LENGTH/2)
            self.assertLess(abs(y-demo.CENTER[1]),.24)

    def test_ten_turns_and_fixed_connections(self):
        straight, wound = demo.wire_points(0), demo.wire_points(1)
        self.assertEqual(straight[0], wound[0])
        self.assertLess(math.dist(straight[-1], wound[-1]), 1e-12)
        helix = [p for p in wound if -demo.LENGTH/2+.03 < p[0] < demo.LENGTH/2-.03]
        angles = [math.atan2(p[2]-demo.CENTER[2], p[1]-demo.CENTER[1]) for p in helix]
        total = sum((b-a+math.pi) % (2*math.pi)-math.pi for a, b in zip(angles, angles[1:]))
        self.assertGreater(total/(2*math.pi), 9.7)
        self.assertGreater(demo.LENGTH/demo.TURNS, 2*.085)

    def test_opening_wire_is_straight_without_loose_bends(self):
        straight = demo.wire_points(0)
        self.assertAlmostEqual(length(straight), 10.)
        self.assertTrue(all(p[1:] == demo.CENTER[1:] for p in straight))
        self.assertTrue(all(a[0] < b[0] for a, b in zip(straight, straight[1:])))

    def test_experiment_starts_with_coil_and_switch_off(self):
        self.assertEqual(demo.coil_fraction(0), 1)
        for t in (0, 2, 5):
            self.assertEqual(demo.current_at(t), 0)
        self.assertEqual(demo.current_at(6), 1)
        self.assertEqual(demo.field_fraction(12), 0)
        self.assertEqual(demo.field_fraction(16), 1)

    def test_current_reversal_reverses_field(self):
        field = demo.field_at(demo.CENTER)
        reverse = demo.field_at(demo.CENTER, current=-1)
        self.assertLess(field[0], 0)  # Left N, right S for conventional current.
        for a, b in zip(field, reverse):
            self.assertAlmostEqual(a, -b)
        self.assertAlmostEqual(demo.current_at(26), 1)
        self.assertEqual(demo.current_at(29), 0)
        self.assertEqual(demo.current_at(32), -1)

    def test_needle_returns_to_earth_field_while_disconnected(self):
        north = demo.NORTH_ANGLE
        self.assertAlmostEqual(demo.compass_angle(1, 0), north)
        for center in demo.COMPASS_CENTERS:
            self.assertAlmostEqual(demo.compass_angle(1, 0, center), north)
            forward, reverse = [demo.needle_angle_at(t, center) for t in (24, 34)]
            # Both north tips point away from left N and toward right S;
            # reversing the supply changes both tips' axial direction.
            self.assertLess(math.cos(forward), 0)
            self.assertGreater(math.cos(reverse), 0)
            separation = abs(math.atan2(math.sin(forward-reverse), math.cos(forward-reverse)))
            self.assertGreater(separation, math.radians(40))
        # Equal-distance end compasses show the same ideal-solenoid deflection.
        for t in (26, 32, 61, 93):
            self.assertAlmostEqual(demo.needle_angle_at(t,demo.COMPASS_CENTERS[0]),
                                   demo.needle_angle_at(t,demo.COMPASS_CENTERS[1]))

    def test_more_turns_and_iron_strengthen_compass_at_fixed_current(self):
        self.assertEqual(demo.coil_fraction(0),1)
        self.assertEqual(demo.DENSE_RADIUS,demo.RADIUS)
        self.assertGreater(demo.LENGTH/demo.DENSE_TURNS,2*demo.WIRE_RADIUS)
        for center in demo.COMPASS_CENTERS:
            angles = [abs(demo.needle_angle_at(t,center)-demo.NORTH_ANGLE) for t in (32,61,93)]
            self.assertLess(angles[0],angles[1])
            self.assertLess(angles[1],angles[2])
        for t in (32,61,93,108):
            self.assertEqual(demo.current_at(t),-1)
        for t in (53,70,100,113):
            self.assertEqual(demo.current_at(t),0)
        a,b = demo.dense_wire_points(0),demo.dense_wire_points(1)
        self.assertLess(math.dist(a[0],b[0]),1e-12)
        self.assertLess(math.dist(a[-1],b[-1]),1e-12)

    def test_compasses_keep_fixed_symmetric_positions(self):
        for center in demo.COMPASS_CENTERS:
            moved = demo.compass_center_at(93,center)
            self.assertEqual(moved,center)
            self.assertEqual(demo.compass_center_at(61,center),center)
            fields = [demo.field_at(demo.compass_center_at(93,c),1,-1,
                                    demo.DENSE_TURNS,demo.DENSE_RADIUS,demo.CORE_GAIN)
                      for c in demo.COMPASS_CENTERS]
            axial = sum(field[0] for field in fields)/2
            expected = math.atan2(demo.EARTH_FIELD[1],demo.EARTH_FIELD[0]+axial)
            self.assertAlmostEqual(demo.needle_angle_at(93,center),expected)
        self.assertEqual(demo.DURATION-demo.APPLICATIONS_START,11)

    @unittest.skipUnless(importlib.util.find_spec("numpy"),"Install requirements-media.txt for vectorized field checks")
    def test_vectorized_field_matches_scalar_segments(self):
        from electromagnetism.ring_field import Segments
        segments = [((0,0,0),(1,0,0)),((1,0,0),(1,1,0))]
        for point in ((.5,.2,.3),(2,0,0),(-1,2,3)):
            actual = Segments(segments).at(point)
            expected = [current_demo.segment_field(point,a,b) for a,b in segments]
            for i in range(3):
                self.assertAlmostEqual(actual[i],sum(v[i] for v in expected))

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
