"""Timing, direction and camera-continuity checks without Blender."""

from pathlib import Path
import sys
import math
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from electromagnetism.motion import current_on, drift_time, electron_position, sample_path, ion_position
from electromagnetism.config import LESSON, ELECTRON_PATH, ELECTRON_HALF_LENGTH, ELECTRON_DRIFT_SPEED
from electromagnetism.camera_path import camera_pose, OVERVIEW


class MotionTests(unittest.TestCase):
    def test_current_only_in_closed_interval(self):
        self.assertFalse(current_on(LESSON.switch_on-0.001))
        self.assertTrue(current_on(LESSON.switch_on))
        self.assertTrue(current_on(LESSON.switch_off-0.001))
        self.assertFalse(current_on(LESSON.switch_off))
        self.assertEqual(LESSON.field_reveal, LESSON.switch_on)

    def test_drift_stops_without_stopping_random_motion(self):
        self.assertEqual(drift_time(LESSON.switch_on-1), 0)
        self.assertEqual(drift_time(LESSON.switch_on+1), 1)
        self.assertEqual(drift_time(LESSON.switch_off+1), LESSON.switch_off-LESSON.switch_on)
        self.assertNotEqual(electron_position(4, 45), electron_position(4, 46))

    def test_particles_stay_on_the_extended_wire_sample(self):
        for seed in range(LESSON.seed, LESSON.seed+LESSON.electrons):
            for tick in range(LESSON.last_frame):
                x, y, z = electron_position(seed, tick/LESSON.fps)
                self.assertTrue(-ELECTRON_HALF_LENGTH <= x <= ELECTRON_HALF_LENGTH)
                self.assertTrue(-1.35 < y < -0.62)
                self.assertTrue(-0.43 < z < 0.59)

    def test_net_drift_is_positive_x(self):
        width = 2*ELECTRON_HALF_LENGTH
        for seed in range(LESSON.electrons):
            start = electron_position(seed, LESSON.switch_on)[0]
            end = electron_position(seed, LESSON.switch_on+1)[0]
            displacement = ((end-start+width/2) % width)-width/2
            self.assertGreater(displacement, ELECTRON_DRIFT_SPEED-.3)
        # Check the displayed drift on every frame, unwrapping the periodic
        # sample boundary; no marker travels backward while current is on.
        for seed in range(LESSON.seed, LESSON.seed+LESSON.electrons):
            for frame in range(LESSON.frame(LESSON.switch_on+1), LESSON.frame(LESSON.microscope_out)):
                a = electron_position(seed, (frame-1)/LESSON.fps)[0]
                b = electron_position(seed, frame/LESSON.fps)[0]
                self.assertGreater((b-a+width/2) % width-width/2, 0)

    def test_external_path_moves_from_negative_towards_positive(self):
        self.assertEqual(sample_path(ELECTRON_PATH, 0), ELECTRON_PATH[0])
        self.assertGreater(sample_path(ELECTRON_PATH, 0.6)[0], sample_path(ELECTRON_PATH, 0.3)[0])
        self.assertLess(sample_path(ELECTRON_PATH, 0.999)[0], 1.1)

    def test_camera_has_no_cut_and_returns_to_original_view(self):
        positions = [camera_pose(t/LESSON.fps)[0] for t in range(LESSON.last_frame)]
        # Measure smoothness relative to distance from the subject: world-unit
        # speed naturally increases as a zoom moves away from a tiny sample.
        for tick, (a,b) in enumerate(zip(positions,positions[1:])):
            target = camera_pose(tick/LESSON.fps)[1]
            self.assertLess(math.dist(a,b)/math.dist(a,target), 0.045)
        returned = camera_pose(LESSON.zoom_out_end)
        self.assertLess(math.dist(returned[0], OVERVIEW[0]), 1e-8)
        self.assertLess(math.dist(returned[1], OVERVIEW[1]), 1e-8)
        self.assertGreater(math.dist(camera_pose(LESSON.zoom_start+2)[0], OVERVIEW[0]), 1)

    def test_lab_frame_ions_never_crowd_when_switch_closes(self):
        base = (2, 0.3, 0.3)
        for frame in range(LESSON.last_frame):
            position = ion_position(base, 3, frame/LESSON.fps)
            self.assertLessEqual(max(abs(a-b) for a,b in zip(base,position)), 0.035001)


if __name__ == "__main__":
    unittest.main()
