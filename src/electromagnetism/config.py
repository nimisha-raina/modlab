"""Edit the lesson's timing, colours and quality here first.

Distances are illustration units, NOT atomic or laboratory measurements.
All timestamps are seconds from the start; frame 1 is time zero.
"""

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "output"
SCENE_NAME = "01 - Electricity makes magnetism"


@dataclass(frozen=True)
class Lesson:
    fps: int = 24
    duration: int = 48
    zoom_start: float = 0.5
    microscope_in: float = 5.0
    switch_move: float = 8.25
    switch_on: float = 9.0
    field_reveal: float = 21.0
    microscope_out: float = 27.0
    zoom_out_end: float = 37.0
    wide_view: float = 42.0
    switch_off: float = 44.0
    electrons: int = 18
    seed: int = 23

    def frame(self, seconds):
        return round(seconds * self.fps) + 1

    @property
    def last_frame(self):
        return self.duration * self.fps


LESSON = Lesson()

# RGBA colours. Labels and shape cues accompany every important colour.
PALETTE = {
    "navy": (0.009, 0.022, 0.049, 1),
    "panel": (0.018, 0.043, 0.074, 1),
    "edge": (0.045, 0.105, 0.15, 1),
    "copper": (0.65, 0.235, 0.075, 1),
    "copper_light": (0.95, 0.46, 0.18, 1),
    "cyan": (0.05, 0.8, 1.0, 1),
    "mint": (0.15, 1.0, 0.66, 1),
    "gold": (1.0, 0.68, 0.12, 1),
    "white": (0.87, 0.96, 1.0, 1),
    "muted": (0.43, 0.62, 0.73, 1),
    "silver": (0.45, 0.58, 0.66, 1),
    "ceramic": (0.64, 0.51, 0.32, 1),
}

QUALITY = {
    "preview": {"resolution": (1280, 720), "samples": 24},
    "final": {"resolution": (1920, 1080), "samples": 64},
}

WIRE_Z = 0.7
SAMPLE_Z = 1.6
# The enlarged teaching model sits INSIDE the actual central wire segment.
# One camera can approach and leave it continuously, without a camera cut.
MICRO_ORIGIN = (0, 2.2, SAMPLE_Z)
MICRO_SCALE = 0.115 / 1.12
# Both close-up particles and circuit markers use this one world-space radius.
# Camera magnification alone changes their apparent size.
ELECTRON_RADIUS = 0.10 * MICRO_SCALE
ELECTRON_HALF_LENGTH = 7.8
ELECTRON_DRIFT_SPEED = 1.15
# Ordered from the negative terminal, along the external conductor, to positive.
ELECTRON_PATH = [(-2.0, -2.2, WIRE_Z), (-5, -2.2, WIRE_Z), (-5, 2.2, SAMPLE_Z),
                 (5, 2.2, SAMPLE_Z), (5, 0.5, WIRE_Z), (5, -2.2, WIRE_Z),
                 (1.0, -2.2, WIRE_Z)]
