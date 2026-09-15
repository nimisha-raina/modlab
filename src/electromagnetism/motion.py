"""Timing and pure mathematics, separated from the objects being animated.

The random-looking motion is a schematic, repeatable teaching illustration.
It is not a molecular dynamics or electric-field simulation.
"""

import math
from .config import LESSON, ELECTRON_HALF_LENGTH, ELECTRON_DRIFT_SPEED


def current_on(seconds):
    return LESSON.switch_on <= seconds < LESSON.switch_off


def drift_time(seconds):
    return max(0.0, min(seconds, LESSON.switch_off) - LESSON.switch_on)


def electron_position(seed, seconds, origin=(0, 0, 0)):
    """Bounded jitter plus +X drift; opposite conventional current.

The periodic X boundary represents a sample from a much longer conductor.
Motion is baked every frame so wrapping never draws a streak across the wire.
"""
    phase = seed * 2.399963
    half = ELECTRON_HALF_LENGTH
    start_x = -half + ((seed-LESSON.seed) % LESSON.electrons)/LESSON.electrons*(2*half)
    jitter_x = 0.09*math.sin(seconds*8.1+phase) + 0.035*math.sin(seconds*17.3-phase)
    x = ((start_x + ELECTRON_DRIFT_SPEED*drift_time(seconds) + jitter_x + half) % (2*half)) - half
    # Front lanes keep the sparse teaching markers clear of the compact ions.
    # Transverse jitter remains visible both before and during net drift.
    y = -0.71 + 0.08*math.sin(seconds*10.7+phase)
    z = (0.48 if seed % 2 else -0.32) + 0.10*math.sin(seconds*12.3-phase)
    # Surface direction markers stay visible on the opaque wire at each end.
    edge = max(0.0, min(1.0, (abs(x)-4.3)/1.0))
    y -= 0.55*edge*edge*(3-2*edge)
    return (x+origin[0], y+origin[1], z+origin[2])


def ion_position(base, seed, seconds):
    phase = seed*1.73
    return tuple(base[axis] + 0.035*math.sin(seconds*(7.3+axis)+phase+axis)
                 for axis in range(3))


def sample_path(points, fraction):
    """Travel at constant speed along an ordered polyline."""
    lengths = [math.dist(a, b) for a, b in zip(points, points[1:])]
    distance = (fraction % 1.0) * sum(lengths)
    for a, b, length in zip(points, points[1:], lengths):
        if distance <= length:
            mix = distance / length
            return tuple(x+(y-x)*mix for x, y in zip(a, b))
        distance -= length
    return points[-1]


def visibility(obj, start, end, last_frame=LESSON.last_frame):
    """Visible on the inclusive [start, end] range in render AND viewport."""
    keys = {1: True, max(1, start): False, end+1: True}
    if start > 1:
        keys[start-1] = True
    keys[end] = False
    for frame, hidden in sorted(keys.items()):
        if frame <= last_frame:
            obj.hide_render = hidden
            obj.hide_viewport = hidden
            obj.keyframe_insert("hide_render", frame=frame)
            obj.keyframe_insert("hide_viewport", frame=frame)


def visible_windows(obj, windows):
    """Several inclusive visibility windows without overwriting earlier keys."""
    for frame in range(1, LESSON.last_frame+1):
        hidden = not any(start <= frame <= end for start, end in windows)
        obj.hide_render = obj.hide_viewport = hidden
        obj.keyframe_insert("hide_render", frame=frame)
        obj.keyframe_insert("hide_viewport", frame=frame)


def key_location(obj, frame, location):
    obj.location = location
    obj.keyframe_insert("location", frame=frame)
