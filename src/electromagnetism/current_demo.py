"""Part 1 timing and compass physics, independent of Blender.

Wire fields use the finite-segment Biot-Savart integral, with a common scale
factor omitted. Multiplier I corresponds to an illustrative 0.50 A display;
the geometry and field scale do not specify a real laboratory calibration.
Earth's horizontal field is chosen perpendicular to the circuit's horizontal
field at the fixed compass position, giving 25 degrees at I and about 43 at 2I.
"""

import math
from .config import ELECTRON_PATH, SAMPLE_Z, WIRE_Z
from .camera_path import WIDE, BOARD, interpolate_pose, smoothstep

SCENE_NAME = "02 - Compass and current"
DURATION = 34
SUMMARY_START = 24
BOARD_ARRIVAL = 26
SUMMARY_POINTS = (
    "1. Electrons drift from negative to positive.",
    "2. Electric current creates a magnetic field.",
    "3. A compass detects the wire's magnetic field.",
    "4. More current: stronger field, greater needle deflection.",
)
FPS = 24
COMPASS_CENTER = (0, 1.45, .28)
PLACEMENT_START = .5
PLACEMENT_END = 5.0
DOUBLE_START = 14.0
RESTORE_START = 21.0
BOARD_VIEW = ((0, -13, 7.5), (0, 7.8, 2.8))
CLOSE_VIEW = ((4, -6, 10), (-2, 1.2, 1.1))
AMMETER_CENTER = (-5, 0, 1.70)
AMMETER_TILT = math.radians(50)
REFERENCE_AMPS = .5


def left_wire_z(y):
    return WIRE_Z+(SAMPLE_Z-WIRE_Z)*(y+2.2)/4.4


# The ammeter covers a real series gap in the left conductor. Short rear
# connections sit behind the dial; the internal current path is idealized.
def meter_world_point(point):
    x, y, z = point
    c, s = math.cos(AMMETER_TILT), math.sin(AMMETER_TILT)
    return (AMMETER_CENTER[0]+x, AMMETER_CENTER[1]+y*c-z*s,
            AMMETER_CENTER[2]+y*s+z*c)


METER_TERMINALS = ((0, -.30, -.18), (0, .30, -.18))
METER_PATH = [(-5, -.42, left_wire_z(-.42)), meter_world_point(METER_TERMINALS[0]),
              meter_world_point(METER_TERMINALS[1]), (-5, .1, left_wire_z(.1))]
CURRENT_PATH = ELECTRON_PATH[:2]+METER_PATH+ELECTRON_PATH[2:]


def meter_angle(amperes):
    """A centre-zero +/-1 A scale: positive current moves the pointer right."""
    return math.pi/2-math.pi/3*amperes


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def segment_field(point, start, end):
    """Field for unit conventional current from start to end; excludes mu0/4pi."""
    length = math.dist(start, end)
    if length == 0:
        return (0., 0., 0.)
    unit = tuple((b-a)/length for a, b in zip(start, end))
    r = tuple(p-a for p, a in zip(point, start))
    along = sum(a*b for a, b in zip(r, unit))
    radial = tuple(a-along*b for a, b in zip(r, unit))
    radius2 = sum(a*a for a in radial)
    if radius2 < 1e-12:
        if along < 0 or along > length:
            return (0., 0., 0.)
        raise ValueError("Field probe must not lie on the wire axis")
    factor = (along/math.sqrt(radius2+along*along)
              - (along-length)/math.sqrt(radius2+(along-length)**2))/radius2
    return tuple(factor*a for a in cross(unit, radial))


def circuit_field(point, current=1):
    # Close the path through the idealized supply; conventional current is
    # opposite the external electron path. The conductor geometry stays fixed.
    path = CURRENT_PATH + [CURRENT_PATH[0]]
    parts = [segment_field(point, b, a) for a, b in zip(path, path[1:])]
    return tuple(current*sum(part[axis] for part in parts) for axis in range(3))


WIRE_FIELD = circuit_field(COMPASS_CENTER)
WIRE_HORIZONTAL = math.hypot(*WIRE_FIELD[:2])
EARTH_STRENGTH = WIRE_HORIZONTAL/math.tan(math.radians(25))
EARTH_FIELD = (-WIRE_FIELD[1]/WIRE_HORIZONTAL*EARTH_STRENGTH,
               WIRE_FIELD[0]/WIRE_HORIZONTAL*EARTH_STRENGTH, 0.)
NORTH_ANGLE = math.atan2(EARTH_FIELD[1], EARTH_FIELD[0])


def compass_angle(current, point=COMPASS_CENTER):
    """A horizontal compass aligns with the horizontal component of total B."""
    field = circuit_field(point, current)
    return math.atan2(EARTH_FIELD[1]+field[1], EARTH_FIELD[0]+field[0])


def current_at(seconds):
    return (1+smoothstep((seconds-DOUBLE_START)/.8)
            - smoothstep((seconds-RESTORE_START)/.8))


def placement_offset(seconds):
    u = smoothstep((seconds-PLACEMENT_START)/(PLACEMENT_END-PLACEMENT_START))
    return (6*(1-u), -2*(1-u), 2*(1-u))


def compass_position(seconds):
    return tuple(a+b for a, b in zip(COMPASS_CENTER, placement_offset(seconds)))


def camera_pose(seconds):
    stops = [(0, WIDE), (.5, WIDE), (4.5, CLOSE_VIEW),
             (9, CLOSE_VIEW), (10.5, BOARD_VIEW), (11.5, BOARD_VIEW),
             (13.5, CLOSE_VIEW), (24, CLOSE_VIEW),
             (BOARD_ARRIVAL, BOARD), (DURATION, BOARD)]
    for (ta, a), (tb, b) in zip(stops, stops[1:]):
        if seconds <= tb:
            return interpolate_pose(a, b, (seconds-ta)/(tb-ta))
    return BOARD
