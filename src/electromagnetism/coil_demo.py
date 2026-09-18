"""Coil and electromagnet timing and magnetic relationships, without Blender."""

import math
from functools import lru_cache
from . import current_demo as circuit
from .wire_winding import points as winding_points, helix
from .camera_path import BOARD, OPENING_WIDE, interpolate_pose, smoothstep
from .config import SAMPLE_Z, ELECTRON_PATH

SCENE_NAME = "03 - Coil and current reversal"
FPS = 24
DURATION = 136
TURNS = 10
RADIUS = .62
LENGTH = 3.2
CENTER = (0, 2.2, SAMPLE_Z)
COMPASS_CENTERS = ((-2.5, 2.2, SAMPLE_Z+.30), (2.5, 2.2, SAMPLE_Z+.30))
COMPASS_CENTER = COMPASS_CENTERS[0]
CLOSE_VIEW = ((.5, -11, 12), (0, .0, 1.3))
WINDING_VIEW = ((0, -3, 8.5), CENTER)
REVERSAL_VIEW = ((1, -13, 13), (0, 0, 1.3))
CLIPS_VIEW = ((.4,-8,7.5),(0,1,1.6))
CORE_VIEW = ((4, -14, 12), (0, 0, 1.3))
SUMMARY_VIEW = ((0, -8, 6.5), (0, 11.08, 3.5))
COIL_START, COIL_END = 9., 14.
FIELD_START, FIELD_END = 18.5, 20.
POLE_START = 20.
OPEN_START, OPEN_END = 0., 0.
CLOSE_START, CLOSE_END = 15., 16.
COMPASS_START, COMPASS_END = 21., 24.
REVERSE_START, REVERSE_END = 34., 39.
CELL_TURN_START, CELL_TURN_END = 35., 38.
DENSE_START, DENSE_END = 51., 56.
DENSE_TURNS, DENSE_RADIUS = 20, .52
WIRE_RADIUS = .065
COMPASS_SCALE = .72
CORE_START, CORE_END = 73., 77.
CORE_GAIN = 3.
CORE_GUIDE_ANGLE = .35
SUMMARY_START, APPLICATIONS_START = 114., 125.
APPLICATIONS_DURATION = 11.
CLIP_FALL_DURATION = 1.2
INSIDE_FIELD_LABEL = "MAGNETIC FIELD INSIDE COIL"
OUTSIDE_FIELD_LABEL = "MAGNETIC FIELD OUTSIDE COIL"


def compass_center_at(seconds, center):
    """Clear the insertion area while keeping measured positions explicit."""
    offset = .22*ramp(seconds, 71, 73)
    return (center[0]+math.copysign(offset, center[0]), center[1], center[2])


def ramp(seconds, start, end):
    return smoothstep((seconds-start)/(end-start))


def dense_fraction(seconds):
    return ramp(seconds, DENSE_START, DENSE_END)


def core_fraction(seconds):
    return ramp(seconds, CORE_START, CORE_END)


def coil_fraction(seconds):
    return smoothstep((seconds-COIL_START)/(COIL_END-COIL_START))


def field_fraction(seconds):
    return smoothstep((seconds-FIELD_START)/(FIELD_END-FIELD_START))


def current_at(seconds):
    # Open the circuit, reverse the cell while disconnected, then close it.
    return (ramp(seconds, 15, 16)-ramp(seconds, 34, 35)-ramp(seconds, 38, 39)
            +ramp(seconds, 50, 51)-ramp(seconds, 58, 59)
            +ramp(seconds, 72, 73)-ramp(seconds, 78, 79)
            +ramp(seconds, 100, 101)-ramp(seconds, 104, 105)+ramp(seconds, 111, 112))


@lru_cache(maxsize=512)
def wire_points(fraction, samples=721):
    """Straight-wire opening and cropped winding diagram; fixed end connections."""
    return winding_points(fraction, CENTER, RADIUS, LENGTH, TURNS, samples)


@lru_cache(maxsize=512)
def dense_wire_points(fraction):
    return helix(CENTER, RADIUS+(DENSE_RADIUS-RADIUS)*fraction, LENGTH,
                 TURNS+(DENSE_TURNS-TURNS)*fraction)


@lru_cache(maxsize=256)
def circuit_fields(point, fraction, turns, radius):
    wire = wire_points(fraction) if turns == TURNS and radius == RADIUS else helix(CENTER, radius, LENGTH, turns)
    path = ELECTRON_PATH[:2]+circuit.METER_PATH+wire+ELECTRON_PATH[4:]
    path += [path[0]]
    def sum_field(path):
        parts = [circuit.segment_field(point, b, a) for a, b in zip(path, path[1:])]
        return tuple(sum(p[axis] for p in parts) for axis in range(3))
    return sum_field(path), sum_field(wire)


def field_at(point, fraction=1, current=1, turns=TURNS, radius=RADIUS, core_gain=1.):
    if current == 0:
        return (0., 0., 0.)
    # Electron route: battery -> meter -> left side -> coil -> right side.
    full, coil = circuit_fields(tuple(point), fraction, turns, radius)
    # Effective core model amplifies the coil contribution only; it leaves
    # circuit branches and Earth's field unchanged. Not a material prediction.
    return tuple(current*(a+(core_gain-1)*b) for a, b in zip(full, coil))


BASE_FIELD = field_at(COMPASS_CENTER)
HORIZONTAL = math.hypot(*BASE_FIELD[:2])
EARTH_STRENGTH = HORIZONTAL/math.tan(math.radians(30))
# One common Earth field for both physical compasses; the red tip follows
# the resultant horizontal field, rather than forcing opposite end needles.
EARTH_FIELD = (0., EARTH_STRENGTH, 0.)
NORTH_ANGLE = math.atan2(EARTH_FIELD[1], EARTH_FIELD[0])


def compass_angle(fraction, current, center=COMPASS_CENTER, turns=TURNS, radius=RADIUS, core_gain=1.):
    field = field_at(center, fraction, current, turns, radius, core_gain)
    return math.atan2(EARTH_FIELD[1]+field[1], EARTH_FIELD[0]+field[0])


def compass_angle_at(seconds, center=COMPASS_CENTER):
    dense, core = dense_fraction(seconds), core_fraction(seconds)
    return compass_angle(coil_fraction(seconds), current_at(seconds), compass_center_at(seconds, center),
                         TURNS+(DENSE_TURNS-TURNS)*dense, RADIUS+(DENSE_RADIUS-RADIUS)*dense,
                         1+(CORE_GAIN-1)*core)


def needle_angle_at(seconds, center=COMPASS_CENTER):
    angle = compass_angle_at(seconds, center)
    settle = ramp(seconds, COMPASS_END, COMPASS_END+1.5)
    delta = math.atan2(math.sin(angle-NORTH_ANGLE), math.cos(angle-NORTH_ANGLE))
    return NORTH_ANGLE+settle*delta


def flow_phase(seconds, sign):
    start, end = (24.,28.) if sign == 1 else (39.,44.)
    return .45*max(0.,min(end-start,seconds-start))


def camera_pose(seconds):
    stops = [(0, OPENING_WIDE), (4, OPENING_WIDE), (9, WINDING_VIEW), (14, WINDING_VIEW),
             (18, CLOSE_VIEW), (28, CLOSE_VIEW), (31, BOARD), (32, BOARD),
             (34, REVERSAL_VIEW), (44, REVERSAL_VIEW), (47, BOARD), (48, BOARD),
             (50, CLOSE_VIEW), (66, CLOSE_VIEW), (69, BOARD), (70, BOARD),
             (72, CORE_VIEW), (80, CORE_VIEW), (83, BOARD), (89, BOARD),
             (92, CORE_VIEW), (94, CORE_VIEW), (97, BOARD), (98, BOARD),
             (100, REVERSAL_VIEW), (105,REVERSAL_VIEW),(107,CLIPS_VIEW),(111,CLIPS_VIEW),
             (113,REVERSAL_VIEW),(114, REVERSAL_VIEW), (117, SUMMARY_VIEW), (DURATION, SUMMARY_VIEW)]
    for (ta, a), (tb, b) in zip(stops, stops[1:]):
        if seconds <= tb:
            return interpolate_pose(a, b, (seconds-ta)/(tb-ta))
    return CLOSE_VIEW


@lru_cache(maxsize=2)
def _solenoid_candidates(turns, radius):
    """Closed meridional guides traced through a finite ten-ring field.

    Axisymmetric rings approximate the helix, excluding connecting leads.
    Compass physics instead uses the complete helical circuit above. Traces
    represent a static resultant field, not physical strings carried by wire.
    """
    rings = []
    for turn in range(turns):
        x = -LENGTH/2+LENGTH*(turn+.5)/turns
        ring = [(x, radius*math.cos(i*2*math.pi/48), radius*math.sin(i*2*math.pi/48))
                for i in range(49)]
        rings.extend(zip(ring, ring[1:]))

    from .ring_field import Segments
    sources = Segments(rings)
    def direction(p):
        vector = sources.at(p)
        norm = math.hypot(vector[0], vector[1])
        return (vector[0]/norm, vector[1]/norm, 0.)

    def trace(seed_radius):
        seed = (0., seed_radius*radius/RADIUS, 0.)
        p, points = seed, [seed]
        step_length = .015
        for step in range(5000):
            a = direction(p)
            b = direction(tuple(v+step_length*d/2 for v,d in zip(p,a)))
            c = direction(tuple(v+step_length*d/2 for v,d in zip(p,b)))
            d = direction(tuple(v+step_length*w for v,w in zip(p,c)))
            p = tuple(v+step_length*(w+2*x+2*y+z)/6
                      for v,w,x,y,z in zip(p,a,b,c,d))
            points.append(p)
            if step > 200 and math.dist(p,seed)<.018:
                break
            if abs(p[0])>8 or abs(p[1])>8:
                raise ValueError("Solenoid guide escaped the drawing region")
        else:
            raise ValueError("Solenoid guide did not close")
        points[-1] = seed
        return points

    # Equal seed gaps do not give equal gaps outside a finite coil. Choose
    # true traced loops by evenly spaced outer extents, rather than bunching
    # separate strength families into narrow bands.
    candidates = [trace(.48+.10*i/48) for i in range(49)]
    candidates.sort(key=lambda line:max(p[1] for p in line),reverse=True)
    return candidates


@lru_cache(maxsize=4)
def solenoid_lines(turns=TURNS, radius=RADIUS, seed_count=5):
    """Closed finite-ring traces selected for evenly spread outer extents."""
    candidates = _solenoid_candidates(turns,radius)
    extents = [max(p[1] for p in line) for line in candidates]
    selected = []
    for i in range(seed_count):
        target = extents[0]+(extents[-1]-extents[0])*i/(seed_count-1)
        index = min(range(len(candidates)),key=lambda j:abs(extents[j]-target))
        selected.append(candidates[index])
    result = []
    for points in selected:
        # Resample each closed trace to matching vertex counts for shape keys.
        distances = [0.]
        for a, b in zip(points, points[1:]):
            distances.append(distances[-1]+math.dist(a, b))
        resampled, cursor = [], 0
        for i in range(192):
            distance = distances[-1]*i/192
            while distances[cursor+1] < distance:
                cursor += 1
            f = (distance-distances[cursor])/(distances[cursor+1]-distances[cursor])
            resampled.append(tuple(a+(b-a)*f for a, b in zip(points[cursor], points[cursor+1])))
        result.append(resampled)
    return result
