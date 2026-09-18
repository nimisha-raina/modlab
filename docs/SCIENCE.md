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
In the current Blender draft, ions and electrons are revealed together only in
the magnified cutaway. Their absence from the overview is a display choice;
conduction electrons remain present throughout the physical copper wire.
The orange spheres denote positive metal ion cores in a free-electron picture.

The particle paths combine repeatable jitter with exaggerated drift, not
calculated collision dynamics. The revised display makes rightward drift faster
and reduces the drawn jitter while current flows so direction is easier to see.
This is a visual convention; actual thermal motion does not decrease when the
switch closes. Ion cores continue vibrating near fixed lattice positions.
Motion, drift and switching times are chosen
for legibility; their relative speeds are not quantitative. Electrons wrap at
the edge of the enlarged sample, representing continuation through a longer
wire. The original reference video also uses surface direction markers in
overview; the revised Blender draft removes those markers.

Three concentric field rings share a centre and perpendicular plane. They illustrate the near-field pattern around the central straight
segment. In the revised overview, six guide locations illustrate local fields
around straight segments on all four sides. Each guide plane is perpendicular
to its own wire, and its arrow follows the right-hand rule for conventional
current. The complete finite circuit has a more complicated field, combining
contributions from all its parts; the circular guides are not numerical traces
of that resultant field. The rings do not measure field strength.

Current and field turn on/off together at the lesson's timescale. In the opening
chapter, switching
transients, circuit inductance and background fields (including Earth's field)
are omitted. An open switch means no **steady current**, not literally no
electric or magnetic field anywhere. An electrical signal propagates much
faster than the electrons' average drift; the animation does not show electrons
racing all the way from the battery before the rest of the wire responds.

A small series current limiter keeps the illustrated circuit from being a
direct battery short. Its value and quantitative voltage/current measurements
are outside the first chapter's scope.

## Compass and current extension

The independent [compass section](PART_01.md) includes a fixed horizontal Earth
field when calculating the needle direction. A horizontal needle aligns with
the horizontal component of the vector sum of Earth and circuit fields. The
circuit field includes the series ammeter leads and is calculated from finite
straight conductors using the
Biot–Savart integral, with conventional current opposite the electron path.

At a fixed point, doubling current doubles the circuit's field. Compass angle
depends on the vector sum: in the perpendicular-field arrangement used here,
`tan(angle) = wire horizontal field / Earth horizontal field`. The illustrative
25° reference angle therefore becomes approximately 43°, not 50°, at twice the
current. The displayed 0.50 A and 1.00 A are illustrative readings; the ammeter
is connected in series through a real conductor gap. Compass placement is
animated using the calculated field at its changing position. These values
are selected for a clear demonstration, not predictions
for a specified laboratory current or geographic location.

Extra drawn guide circles indicate a stronger field. Magnetic field lines are
a representation, not physical strands. Later coil demonstrations should show
the combined field changing with conductor geometry, not strands literally
winding together. The coil should use insulated wire and a soft iron core for
the switch-off demonstration.

The first-case pullback preserves the three circles at the magnified wire
location. Five other sites complete the six-location layout. The eight drawn
circles become sixteen at twice the current; this count is an illustration,
not a measured number of lines. The compass arc and integer-degree readout
show deflection from its fixed Earth-field north reference. Their 25°/43°
comparison uses the same field calculation as the physical needle.

## Sources used for fact checking

The separate [coil and reversal case](PART_02.md) begins with ten spaced,
enamel-coated turns already formed. A finite-ring approximation supplies closed
resultant field guides in several meridional planes, with S→N arrows inside and
N→S outside. Two concentric circles at every displayed local site reinforce that
all current-carrying branches have circular fields; their count and radius are
illustrative. White arrows follow conventional current from positive to negative.
The equidistant end compasses use the averaged axial coil contribution and one
common Earth field, giving equal deflection in this ideal symmetric-solenoid
comparison. The red north-seeking tips point away from the coil's N end and toward
its S end; they need not point in opposite directions in the laboratory view. Opening the switch removes
the coil contribution and leaves the needle following Earth's field. Turning
the disconnected cell and closing the switch reverses current, coil field and
poles. Fixed meter leads give −0.50 A after reversal, with unchanged magnitude.
A centre-zero analogue scale allows the pointer to show this signed reversal.
The circuit is open in the initial complete-coil view, then closes to reveal
paired local upper/lower contributions and their resultant pattern. The camera
orbits right to show the field-guide depth, then returns to the front. The field
is similar to a bar magnet's, with poles while current flows;
the air-core coil does not become a permanent bar magnet. The guide transition
illustrates addition of fields, not physical strands moving and joining.

- [OpenStax, Model of Conduction in Metals](https://openstax.org/books/university-physics-volume-2/pages/9-2-model-of-conduction-in-metals):
  conduction electrons, random motion, drift, positive ion lattice and the
  distinction between electrical-signal speed and drift speed.
- [OpenStax, Magnetic Field Due to a Thin Straight Wire](https://openstax.org/books/university-physics-volume-2/pages/12-2-magnetic-field-due-to-a-thin-straight-wire):
  circular magnetic field lines, right-hand rule and current/distance dependence.
- [KET Virtual Physics Labs, Magnetic Fields](https://www.webassign.net/question_assets/ketphysvl1/lab_13/manual.html):
  compass deflection from the combined wire and Earth fields and the tangent
  relationship for perpendicular fields.
- [OpenStax, Solenoids and Toroids](https://openstax.org/books/university-physics-volume-2/pages/12-6-solenoids-and-toroids):
  combined fields of turns and internal direction from conventional current.
- [OpenStax, Magnetic Fields and Lines](https://openstax.org/books/university-physics-volume-2/pages/11-2-magnetic-fields-and-lines):
  closed magnetic field lines and their direction at north and south poles.
- [Blender Python API](https://docs.blender.org/api/current/): procedural scene
  creation and built-in animation. The installed Blender 5.2.1 API is also
  checked directly during local scene generation and validation.

Lesson text, geometry and styling are original; no textbook diagrams or
passages are copied into the animation.

## Reference-frame clarification

The lesson stays in the laboratory frame. A deliberately labelled change to an
electron-following reference frame is a different, valid lesson; see
[RELATIVITY.md](RELATIVITY.md) for assumptions and the proposed teaching sequence.

## Extended coil and iron-core comparison

Case 2 also changes 10 turns to 20 at fixed axial length, with smaller diameter
and smaller gaps. The regulated supply keeps current magnitude fixed; changing
both geometry parameters does not isolate turn count as a controlled experiment.
Compass needles in the equal-distance comparison use the symmetric axial average
and one shared Earth field; complete-circuit calculations remain documented for
the rest of the scene. Iron-core strength is an illustrative gain on the coil contribution, not a permeability or
hysteresis simulation. The magnetic-region board model shows directions aligning,
not atoms physically moving. Regions sit inside a nail outline. In the reversed
winding, electrons move right to left and the internal field points right;
magnetic north tips align with that internal field. Winding sense is essential
when relating electron flow to the axial field. Compass positions move outward
for insertion, and readings use those actual positions with the same Earth field.
Low-remanence soft iron is assumed for clip release.
See [PART_02.md](PART_02.md) for detailed limits and timing.

The dynamic microphone uses a moving coil in a permanent magnet's field to induce
a signal ([Shure explanation](https://service.shure.com/articles/en_US/Knowledge/difference-between-a-dynamic-and-condenser-microphone)).
It belongs under uses of electromagnetism rather than uses of powered iron-core
electromagnets. MRI employs strong magnetic fields
([NIBIB](https://www.nibib.nih.gov/science-education/science-topics/magnetic-resonance-imaging-mri));
its illustrated cutaway is conceptual, not a manufacturer's construction drawing.
