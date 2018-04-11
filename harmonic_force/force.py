# Copyright (c) 2018 Malcolm Ramsay

import hoomd
from harmonic_force import _harmonic_force


class HarmonicForce(hoomd.compute._compute):
    """Harmonic Force"""
    def __init__(self, group, lattice_positions, lattice_orientations, force_constant):
        hoomd.util.print_status_line()

        # initialize base class
        _force.__init__(self)

        # initialize the reflected c++ class
        self.cpp_force = _harmonic_force.HarmonicForceCompute(
            hoomd.context.current.system_definition,
            group.cpp_group,
            lattice_positions,
            lattice_orientations,
            force_constant,
        )

        self.group = group
        self.lattice_positions = lattice_positions
        self.lattice_orientations = lattice_orientations
        self.force_constant = force_constant

        hoomd.context.current.system.addCompute(self.cpp_force, self.force_name);
