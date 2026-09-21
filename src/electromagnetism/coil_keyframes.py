"""Source-frame sampling: every moving frame plus stationary hold boundaries."""
from . import coil_demo as demo


def frames(*intervals):
    selected = {1,demo.DURATION*demo.FPS}
    for start,end in intervals:
        a,b = round(start*demo.FPS)+1,round(end*demo.FPS)+1
        selected.update(range(max(1,a-1),min(demo.DURATION*demo.FPS,b+1)+1))
    return sorted(selected)


CURRENT = tuple((a,b) for a,b,_ in demo.coil_switch.TRAVEL)
