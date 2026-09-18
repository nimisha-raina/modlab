"""Centre lines for fixed-connection straight and helical wire configurations."""

import math


def length(points):
    return sum(math.dist(a, b) for a, b in zip(points, points[1:]))


def resample(points, count):
    """Use equal arc-length positions so markers follow the same wire material."""
    distances = [0.]
    for a, b in zip(points, points[1:]):
        distances.append(distances[-1]+math.dist(a, b))
    result, cursor = [], 0
    for i in range(count):
        distance = distances[-1]*i/(count-1)
        while cursor < len(points)-2 and distances[cursor+1] < distance:
            cursor += 1
        f = (distance-distances[cursor])/(distances[cursor+1]-distances[cursor])
        result.append(tuple(a+(b-a)*f for a, b in zip(points[cursor], points[cursor+1])))
    result[0], result[-1] = points[0], points[-1]
    return result


def helix(center, radius, span, turns, samples=721):
    """Continuous helix and fixed end connections, including fractional turns."""
    final = []
    end_y, end_z = radius*math.cos(math.tau*turns), radius*math.sin(math.tau*turns)
    for i in range(1441):
        t = i/1440
        if t < .1:
            u = t/.1
            wound = (-5+(5-span/2)*u, center[1]+radius*u, center[2])
        elif t > .9:
            u = (t-.9)/.1
            wound = (span/2+(5-span/2)*u, center[1]+end_y*(1-u), center[2]+end_z*(1-u))
        else:
            u = (t-.1)/.8
            angle = math.tau*turns*u
            wound = (-span/2+span*u, center[1]+radius*math.cos(angle), center[2]+radius*math.sin(angle))
        final.append(wound)
    return resample(final, samples)


def points(fraction, center, radius, span, turns, samples=721):
    """Interpolate the viewed wire section into a ten-turn helix.

    The camera crops the surrounding supply wire throughout winding. This
    diagram compares configurations; it does not simulate stretching copper.
    Thickness and end connections stay fixed, and the final helix is physical.
    """
    wound = helix(center, radius, span, turns, samples)
    straight = [(-5+10*i/(samples-1), center[1], center[2]) for i in range(samples)]
    return [tuple(a+(b-a)*fraction for a, b in zip(start, end))
            for start, end in zip(straight, wound)]
