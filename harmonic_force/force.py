# Copyright (c) 2018 Malcolm Ramsay

import hoomd
from hoomd.md.force import _force

from ._harmonic_force import HarmonicForceCompute as cpp_HarmonicForceCompute


class HarmonicForceCompute(_force):
    """Harmonic Force"""
    def __init__(self, group, lattice_positions, lattice_orientations, translational_force_constant,
                 rotational_force_constant):
        hoomd.util.print_status_line()
        hoomd.context.msg.notice(2, 'Setting up HarmonicForceCompute\n')

        # initialize base class
        super().__init__()

        # initialize the reflected c++ class
        self.cpp_force = cpp_HarmonicForceCompute(
            hoomd.context.current.system_definition,
            group.cpp_group,
            [tuple(row) for row in lattice_positions],
            [tuple(row) for row in lattice_orientations],
            translational_force_constant,
            rotational_force_constant
        )

        self.group = group
        self.lattice_positions = lattice_positions
        self.lattice_orientations = lattice_orientations
        self.translational_force_constant = translational_force_constant
        self.rotational_force_constant = rotational_force_constant

        hoomd.context.current.system.addCompute(self.cpp_force, self.force_name)
        hoomd.context.msg.notice(2, 'Forces added to system\n')

    def update_coeffs(self):
        pass
