"""Convert storyboard seconds into narrated-video seconds (no bpy required)."""


def map_time(seconds, timing):
    if timing is None:
        return seconds
    for clip in timing["segments"]:
        if seconds <= clip["end"]:
            fraction = max(0, (seconds-clip["start"])/(clip["end"]-clip["start"]))
            return clip["target_start"] + fraction*(clip["target_end"]-clip["target_start"])
    return timing["duration"]
