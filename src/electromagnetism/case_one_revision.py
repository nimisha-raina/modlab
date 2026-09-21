"""Case 1 revision geometry and camera poses; the frozen source stays intact."""
import math
from .camera_path import MICRO_VIEW, OVERVIEW, interpolate_pose
from .config import MICRO_ORIGIN
from .tutor_timing import source_time
from .camera_path import opening_pose


def orbit_pose():
    dx,dy,dz=(a-b for a,b in zip(MICRO_VIEW[0],MICRO_ORIGIN))
    radius=math.hypot(dx,dy)*1.12
    return ((MICRO_ORIGIN[0]+radius*math.sin(math.radians(60)),
             MICRO_ORIGIN[1]-radius*math.cos(math.radians(60)),
             MICRO_ORIGIN[2]+dz*1.12),MICRO_ORIGIN)


def camera_pose(seconds):
    if seconds<23:return opening_pose(source_time(seconds))
    if seconds<28:return interpolate_pose(MICRO_VIEW,orbit_pose(),(seconds-23)/5)
    if seconds<31:return orbit_pose()
    if seconds<41:return interpolate_pose(orbit_pose(),OVERVIEW,(seconds-31)/10,'sample_until_wide')
    return opening_pose(source_time(seconds))


def conventional_segments():
    # External conventional current: positive terminal, switch, resistor,
    # back copper branch (-X), ammeter, negative terminal.
    return [((1.25,-2.2,.93),(1.8,-2.2,.93)),
            ((4.6,-2.2,.93),(5,-1.7,.93)),
            ((5,.75,1.08),(5,1.45,1.42)),
            ((3.9,2.2,1.85),(2.9,2.2,1.85)),
            ((-2.8,2.2,1.85),(-3.8,2.2,1.85)),
            ((-5,1.8,1.72),(-5,1.2,1.58)),
            ((-5,-1.1,1.16),(-5,-1.8,1.0)),
            ((-4.2,-2.2,.93),(-3.2,-2.2,.93))]
