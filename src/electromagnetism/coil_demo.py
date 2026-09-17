"""Six-turn coil timing and magnetic relationships, without Blender imports."""

import math
from . import current_demo as circuit
from .camera_path import BOARD, interpolate_pose, smoothstep
from .config import SAMPLE_Z, ELECTRON_PATH

SCENE_NAME = "03 - Coil and current reversal"
FPS = 24
DURATION = 28
TURNS = 6
RADIUS = .62
LENGTH = 3.2
CENTER = (0, 2.2, SAMPLE_Z)
COMPASS_CENTER = (-2.55, 1.65, .28)
CLOSE_VIEW = ((.5, -9, 11), (-1.3, 1.3, 1.1))
REVERSAL_VIEW = ((2, -11, 10), (-.4, 0, 1))
COIL_START, COIL_END = 5., 11.
FIELD_START, FIELD_END = 11., 15.
REVERSE_START, REVERSE_END = 22., 25.


def coil_fraction(seconds):
    return smoothstep((seconds-COIL_START)/(COIL_END-COIL_START))


def field_fraction(seconds):
    return smoothstep((seconds-FIELD_START)/(FIELD_END-FIELD_START))


def current_at(seconds):
    # Open the circuit, reverse the cell while disconnected, then close it.
    return 1-smoothstep((seconds-REVERSE_START)/.5)-smoothstep((seconds-24.5)/.5)


def wire_points(fraction, samples=361):
    """Morph a teaching diagram from a straight span to a spaced six-turn helix.

    End connections stay fixed. This diagram represents reconfiguring a longer
    copper segment; interpolated length is not a material-stretch simulation.
    The main helical section has exactly six complete turns and separated turns.
    """
    points = []
    for i in range(samples):
        t = i/(samples-1)
        straight = (-5+10*t, CENTER[1], CENTER[2])
        if t < .1:
            u = t/.1
            wound = (-5+(5-LENGTH/2)*u, CENTER[1]+RADIUS*u, CENTER[2])
        elif t > .9:
            u = (t-.9)/.1
            wound = (LENGTH/2+(5-LENGTH/2)*u, CENTER[1]+RADIUS*(1-u), CENTER[2])
        else:
            u = (t-.1)/.8
            angle = 2*math.pi*TURNS*u
            wound = (-LENGTH/2+LENGTH*u, CENTER[1]+RADIUS*math.cos(angle),
                     CENTER[2]+RADIUS*math.sin(angle))
        points.append(tuple(a+(b-a)*fraction for a, b in zip(straight, wound)))
    return points


def field_at(point, fraction=1, current=1):
    # Electron route: battery -> meter -> left side -> coil -> right side.
    path = ELECTRON_PATH[:2]+circuit.METER_PATH+wire_points(fraction)+ELECTRON_PATH[4:]
    path += [path[0]]
    parts = [circuit.segment_field(point, b, a) for a, b in zip(path, path[1:])]
    return tuple(current*sum(p[axis] for p in parts) for axis in range(3))


BASE_FIELD = field_at(COMPASS_CENTER)
HORIZONTAL = math.hypot(*BASE_FIELD[:2])
EARTH_STRENGTH = HORIZONTAL/math.tan(math.radians(35))
EARTH_FIELD = (-BASE_FIELD[1]/HORIZONTAL*EARTH_STRENGTH,
               BASE_FIELD[0]/HORIZONTAL*EARTH_STRENGTH, 0.)
NORTH_ANGLE = math.atan2(EARTH_FIELD[1], EARTH_FIELD[0])


def compass_angle(fraction, current):
    field = field_at(COMPASS_CENTER, fraction, current)
    return math.atan2(EARTH_FIELD[1]+field[1], EARTH_FIELD[0]+field[0])


def camera_pose(seconds):
    stops = [(0, BOARD), (2, BOARD), (5, CLOSE_VIEW), (16, CLOSE_VIEW),
             (18, BOARD), (19, BOARD), (22, CLOSE_VIEW),
             (22.8, REVERSAL_VIEW), (24.5, REVERSAL_VIEW),
             (26, CLOSE_VIEW), (DURATION, CLOSE_VIEW)]
    for (ta, a), (tb, b) in zip(stops, stops[1:]):
        if seconds <= tb:
            return interpolate_pose(a, b, (seconds-ta)/(tb-ta))
    return CLOSE_VIEW


def solenoid_lines():
    """Closed meridional guides traced through a finite six-ring field.

    Axisymmetric rings approximate the helix, excluding connecting leads.
    Compass physics instead uses the complete helical circuit above. Traces
    represent a static resultant field, not physical strings carried by wire.
    """
    rings = []
    for turn in range(TURNS):
        x = -LENGTH/2+LENGTH*(turn+.5)/TURNS
        ring = [(x, RADIUS*math.cos(i*2*math.pi/48), RADIUS*math.sin(i*2*math.pi/48))
                for i in range(49)]
        rings.extend(zip(ring, ring[1:]))

    def direction(p):
        values = [circuit.segment_field(p, a, b) for a, b in rings]
        vector = tuple(sum(v[k] for v in values) for k in range(3))
        norm = math.hypot(vector[0], vector[1])
        return (vector[0]/norm, vector[1]/norm, 0.)

    result = []
    for radius in (.50, .55, .59):
        seed = (0., radius, 0.)
        p, points = seed, [seed]
        for step in range(2000):
            a = direction(p)
            mid = tuple(v+.02*d for v, d in zip(p, a))
            b = direction(mid)
            p = tuple(v+.04*d for v, d in zip(p, b))
            points.append(p)
            if step > 100 and math.dist(p, seed) < .045:
                break
            if abs(p[0]) > 8 or abs(p[1]) > 8:
                raise ValueError("Solenoid guide escaped the drawing region")
        else:
            raise ValueError("Solenoid guide did not close")
        # Resample each closed trace to matching vertex counts for shape keys.
        points[-1] = seed
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
