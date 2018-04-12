# hoomd-harmonic-force

This is a hoomd plugin which uses a harmonic force to constrain
the position and orientation of the particles to a desired position.


## Installation

The recommended method of installing this plug is with conda

```shell
$ conda install malramsay::hoomd-harmonic-force
```

This package has hoomd as a dependency,
and will install it into the environment if not already installed.

This plugin currently only supports python 3.6 and numpy 1.14
since that is what I am using for my research.

## Use in simulations

The package defines a single class `HarmonicForceCompute`
which computes a force at each timestep
returning particles to their intended position and orientation.
An example of use is shown below;

```python3
import hoomd
from hoomd.harmonic_force import HarmonicForceCompute

hoomd.context.initialize()
sys = hoomd.init.create_lattice(unitcell=hoomd.lattice.unitcell.sq(a=2), n=5)
pairs = hoomd.md.pair.lj(2.5, nlist=hoomd.md.nlist.cell())
pairs.pair_coeff.set("A", "A", epsilon=1.0, sigma=1.0)
hoomd.md.update.enforce2d()
hoomd.md.integrate.mode_standard(dt=0.005)
hoomd.md.integrate.nvt(group, kT=1, tau=1)
snap_init = sys.take_snapshot()

intended_position = snap.particles.position
translational_force_constant = 1
intended_orientation = snap.particles.orientation
rotational_force_constant = 0

HarmonicForceCompute(
    hoomd.group.all(),
    intended_position,
    intended_orientation,
    translational_force_constant,
    rotational_force_constant,
)

hoomd.run(100)
```

This example will keep the particles vibrating about the square lattice they are created on.

## Limitations


This code is research code,
and as such there are no guarantees of correctness or speed.
I don't completely understand the quaternion maths,
so some guidance in that aspect would be appreciated,
particularly with regards to the performance.

Currently the code is only suitable for investigating the free energy
of molecules with no rotational symmetry.
Molecules which are rotationally symmetric
should have an equal energy at all symmetric points.
Since I am only working in 2D with molecules
that are asymmetric this is not currently an presenting an problem.
