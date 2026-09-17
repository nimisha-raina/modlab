"""A continuous camera journey. Pure Python makes continuity easy to check."""

import math
from .config import LESSON, MICRO_ORIGIN, MICRO_SCALE

OVERVIEW = ((3, -20, 16), (0, 0, 0.5))
WIDE = ((12, -24, 15), (0, 1.7, 1))
BOARD = ((0, -8, 6.5), (0, 11.08, 4.15))
OPENING_WIDE = ((4, -29, 20), (0, 3.7, 1.8))


def smoothstep(value):
    t = max(0.0, min(1.0, value))
    return t*t*(3-2*t)


def mix(a, b, fraction):
    return tuple(x+(y-x)*fraction for x, y in zip(a, b))


def closeup(offset):
    return (tuple(c+s*MICRO_SCALE for c, s in zip(MICRO_ORIGIN, offset)), MICRO_ORIGIN)


MICRO_VIEW = closeup((2, -15, 8))
FIELD_VIEW = closeup((8, -20, 11))


def interpolate_pose(a, b, fraction, focus="normal"):
    """Geometric distance interpolation avoids saving all zoom for the end."""
    u = smoothstep(fraction)
    # Keep the sample centred while it is still large in the picture. Reframe
    # to the whole circuit only when the camera has pulled far enough back.
    target_u = u
    if focus == "sample_early":
        target_u = 1-(1-u)**3
    elif focus == "sample_until_wide":
        target_u = smoothstep((u-0.60)/0.40)
    target = mix(a[1], b[1], target_u)
    da = tuple(x-y for x, y in zip(a[0], a[1]))
    db = tuple(x-y for x, y in zip(b[0], b[1]))
    la, lb = math.sqrt(sum(x*x for x in da)), math.sqrt(sum(x*x for x in db))
    direction = mix(tuple(x/la for x in da), tuple(x/lb for x in db), u)
    norm = math.sqrt(sum(x*x for x in direction))
    distance = math.exp(math.log(la)*(1-u)+math.log(lb)*u)
    location = tuple(t+d/norm*distance for t, d in zip(target, direction))
    return location, target


def camera_pose(seconds):
    stops = [(0, OVERVIEW), (LESSON.zoom_start, OVERVIEW),
             (LESSON.microscope_in, MICRO_VIEW), (LESSON.field_view_start, MICRO_VIEW),
             (LESSON.field_view_end, FIELD_VIEW), (LESSON.microscope_out, FIELD_VIEW),
             (LESSON.zoom_out_end, OVERVIEW), (LESSON.wide_view, WIDE),
             (LESSON.duration, WIDE)]
    for (ta, a), (tb, b) in zip(stops, stops[1:]):
        if seconds <= tb:
            focus = "normal"
            if ta == LESSON.zoom_start:
                focus = "sample_early"
            elif ta == LESSON.microscope_out:
                focus = "sample_until_wide"
            return interpolate_pose(a, b, (seconds-ta)/(tb-ta), focus)
    return WIDE


def field_guide_scale(seconds):
    """Select larger guide circles during pullback so the field stays legible.

    Guide radii are illustrative, not a propagating wave or a field-strength
    measurement. Every displayed circle still lies in a plane normal to wire X.
    """
    u = smoothstep((seconds-LESSON.microscope_out)/(LESSON.zoom_out_end-LESSON.microscope_out))
    return MICRO_SCALE+(0.5-MICRO_SCALE)*u


def opening_pose(seconds):
    """Show board and full circuit together, then approach the copper model."""
    if seconds >= LESSON.microscope_in:
        return camera_pose(seconds)
    stops = [(0, OPENING_WIDE), (LESSON.zoom_start, OPENING_WIDE), (LESSON.microscope_in, MICRO_VIEW)]
    for (ta, a), (tb, b) in zip(stops, stops[1:]):
        if seconds <= tb:
            return interpolate_pose(a, b, (seconds-ta)/(tb-ta),
                                    "sample_early" if ta == LESSON.zoom_start else "normal")
