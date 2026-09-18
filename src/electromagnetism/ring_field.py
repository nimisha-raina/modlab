"""Vectorized finite-segment field for fast closed solenoid guide tracing."""

import numpy as np


class Segments:
    def __init__(self, segments):
        self.starts = np.array([a for a, _ in segments], dtype=float)
        ends = np.array([b for _, b in segments], dtype=float)
        vectors = ends-self.starts
        self.lengths = np.linalg.norm(vectors, axis=1)
        self.units = vectors/self.lengths[:, None]

    def at(self, point):
        r = np.asarray(point)-self.starts
        along = np.sum(r*self.units, axis=1)
        radial = r-along[:, None]*self.units
        radius2 = np.sum(radial*radial, axis=1)
        on_axis = radius2 < 1e-12
        if np.any(on_axis & (along >= 0) & (along <= self.lengths)):
            raise ValueError("Field probe lies on a source segment")
        safe = np.where(on_axis, 1., radius2)
        factor = (along/np.sqrt(safe+along**2)
                  -(along-self.lengths)/np.sqrt(safe+(along-self.lengths)**2))/safe
        factor[on_axis] = 0.
        return np.sum(factor[:, None]*np.cross(self.units, radial), axis=0)
