"""Map the reviewed animation to the spoken apparatus tour and shorter overview."""

STOPS = ((0, 0), (3, 10), (11, 18), (14, 23), (32, 41), (42, 48), (68, 74), (76, 86))


def interpolate(seconds, stops):
    for (a, x), (b, y) in zip(stops, stops[1:]):
        if seconds <= b:
            return x + (seconds - a) * (y - x) / (b - a)
    a, x = stops[-1]
    return x + seconds - a


def lesson_time(source_seconds):
    return interpolate(source_seconds, STOPS)


def source_time(lesson_seconds):
    return interpolate(lesson_seconds, tuple((b, a) for a, b in STOPS))
