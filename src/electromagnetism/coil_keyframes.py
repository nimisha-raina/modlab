"""Source-frame sampling: every moving frame plus stationary hold boundaries."""
from . import coil_demo as demo


def frames(*intervals):
    selected = {1,demo.DURATION*demo.FPS}
    for start,end in intervals:
        a,b = round(start*demo.FPS)+1,round(end*demo.FPS)+1
        selected.update(range(max(1,a-1),min(demo.DURATION*demo.FPS,b+1)+1))
    return sorted(selected)


CURRENT = ((15,16),(34,35),(38,39),(50,51),(58,59),(72,73),
           (78,79),(100,101),(104,105),(111,112))
