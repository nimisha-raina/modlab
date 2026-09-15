# Science behind the teaching model

## What the first chapter teaches

- Copper already has mobile conduction electrons. The battery supplies energy
  and maintains a potential difference; it does not create a fresh population
  of electrons inside an initially empty wire.
- Positive metal ion cores vibrate near their lattice positions. Mobile
  electrons have random motion even before there is a steady current.
- Closing the external circuit establishes an electric field that produces net
  electron drift. In this scene that drift is left to right through the top
  straight wire: from the battery's negative side towards its positive side.
- Conventional current in that wire has the opposite direction. The magnetic
  field arrows use the right-hand rule with **conventional current**.
- Moving electric charges produce magnetic fields. For this lesson, the
  coordinated flow gives a steady field around the wire. Atomic vibration or
  collisions are not offered as the cause of magnetism.

## Deliberate simplifications

This is a schematic teaching animation, not a microscopic simulation. The wire
shell, ions and electrons have exaggerated sizes and spacing. The lattice is
drawn as a compact, easy-to-read grid, not copper's real face-centred cubic crystal.
Electrons are shown as dots without depicting orbitals or quantum behaviour.
The orange spheres denote positive metal ion cores in a free-electron picture.

The particle paths combine repeatable jitter with exaggerated drift, not
calculated collision dynamics. Motion, drift and switching times are chosen
for legibility; their relative speeds are not quantitative. Electrons wrap at
the edge of the enlarged sample, representing continuation through a longer
wire. Circuit dots are direction markers drawn on the wire's surface so they
are visible; this does not mean DC conduction occurs only on that surface.

Three concentric field rings share a centre and perpendicular plane. They illustrate the near-field pattern around the central straight
segment. The complete finite circuit has a more complicated field, including
contributions from its other parts. The rings do not measure field strength.

Current and field turn on/off together at the lesson's timescale. Switching
transients, circuit inductance and background fields (including Earth's field)
are omitted. An open switch means no **steady current**, not literally no
electric or magnetic field anywhere. An electrical signal propagates much
faster than the electrons' average drift; the animation does not show electrons
racing all the way from the battery before the rest of the wire responds.

A small series current limiter keeps the illustrated circuit from being a
direct battery short. Its value and quantitative voltage/current measurements
are outside the first chapter's scope.

## Sources used for fact checking

- [OpenStax, Model of Conduction in Metals](https://openstax.org/books/university-physics-volume-2/pages/9-2-model-of-conduction-in-metals):
  conduction electrons, random motion, drift, positive ion lattice and the
  distinction between electrical-signal speed and drift speed.
- [OpenStax, Magnetic Field Due to a Thin Straight Wire](https://openstax.org/books/university-physics-volume-2/pages/12-2-magnetic-field-due-to-a-thin-straight-wire):
  circular magnetic field lines, right-hand rule and current/distance dependence.
- [Blender Python API](https://docs.blender.org/api/current/): procedural scene
  creation and built-in animation. The installed Blender 5.2.1 API is also
  checked directly during local scene generation and validation.

Lesson text, geometry and styling are original; no textbook diagrams or
passages are copied into the animation.

## Reference-frame clarification

The lesson stays in the laboratory frame. A deliberately labelled change to an
electron-following reference frame is a different, valid lesson; see
[RELATIVITY.md](RELATIVITY.md) for assumptions and the proposed teaching sequence.
