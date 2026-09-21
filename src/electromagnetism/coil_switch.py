"""One electrical contact state shared by the circuit, fields and explanations."""
from .camera_path import smoothstep

# Mechanical travel is separate from conduction: an open contact carries no
# current, even while the blade is approaching the terminal.
TRAVEL = ((5,6,True),(26,27,False),(31,32,True),(50,51,False),
          (58,59,True),(66,67,False),(73,74,True),(80,81,False),
          (85,86,True),(99,100,False),(102,103,True),(111,112,False))
CLOSED = ((6,26,1),(32,50,-1),(59,66,-1),(74,80,-1),
          (86,99,-1),(103,111,-1))


def current(seconds):
    return next((sign for start,end,sign in CLOSED if start<=seconds<=end),0)


def closure(seconds):
    value = 0.
    for start,end,closing in TRAVEL:
        if seconds < start:
            break
        progress = smoothstep((seconds-start)/(end-start))
        value = progress if closing else 1-progress
    return value
