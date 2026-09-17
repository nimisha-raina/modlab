"""Local field-guide locations along the straight circuit segments.

Directions follow the conductor's electron path. Conventional current is
opposite. These circles illustrate local wire contributions, not traced lines
of the complete circuit's resultant field.
"""

from .config import SAMPLE_Z, WIRE_Z, MICRO_ORIGIN

# name, centre, electron direction: two sites on each long side, one per short.
OVERVIEW_GUIDES = (
    ("Far left", (-2.7, 2.2, SAMPLE_Z), (1, 0, 0)),
    ("Far right", (2.7, 2.2, SAMPLE_Z), (1, 0, 0)),
    ("Near left", (-3.6, -2.2, WIRE_Z), (-1, 0, 0)),
    ("Near right", (1.5, -2.2, WIRE_Z), (-1, 0, 0)),
    ("Left side", (-5, 0, (WIRE_Z+SAMPLE_Z)/2), (0, 4.4, SAMPLE_Z-WIRE_Z)),
    ("Right side", (5, 1.35, (WIRE_Z+SAMPLE_Z)/2), (0, -1.7, WIRE_Z-SAMPLE_Z)),
)

OVERVIEW_RADIUS = .55
SAMPLE_RADII = (1.20, 1.53, 1.86)
SAMPLE_OVERVIEW_SCALE = .5


def with_ammeter():
    """Keep the left guide on copper above the series-meter insertion gap."""
    return tuple((name, (-5, 1.35, center[2]+.9*1.35/4.4) if name == "Left side" else center, direction)
                 for name, center, direction in OVERVIEW_GUIDES)


def first_case_guides():
    """Keep the magnified site's three circles as one of six circuit locations."""
    return tuple((name, MICRO_ORIGIN if name == "Far left" else center, direction)
                 for name, center, direction in with_ammeter())


def comparison_radii(name):
    """Baseline and added guide radii; doubled count is a drawing convention."""
    if name == "Far left":
        baseline = tuple(r*SAMPLE_OVERVIEW_SCALE for r in SAMPLE_RADII)
        return baseline, tuple(r+.075 for r in baseline)
    return (OVERVIEW_RADIUS,), (.78,)
