#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Malcolm Ramsay <malramsay64@gmail.com>
#
# Distributed under terms of the MIT license.

"""Test appplying the harmonic force to a simulation."""

import hoomd
import numpy as np
import pytest
from hoomd.harmonic_force import HarmonicForceCompute


@pytest.fixture
def square_lattice():
    with hoomd.context.initialize():
        yield hoomd.init.create_lattice(
            unitcell=hoomd.lattice.sq(a=2.0),
            n=5)


def test_simple(square_lattice):
    snap = square_lattice.take_snapshot()
    HarmonicForceCompute(
        hoomd.group.all(),
        [tuple(row) for row in snap.particles.position],
        [tuple(row) for row in snap.particles.orientation],
        1.
    )
    hoomd.run(10)

def test_no_diffusion(square_lattice):
    snap_init = square_lattice.take_snapshot()
    pairs = hoomd.md.pair.lj(2.5, nlist=hoomd.md.nlist.cell())
    pairs.pair_coeff.set('A', 'A', epsilon=1.0, sigma=1.0)
    HarmonicForceCompute(
        hoomd.group.all(),
        [tuple(row) for row in snap_init.particles.position],
        [tuple(row) for row in snap_init.particles.orientation],
        1.
    )
    hoomd.md.update.enforce2d()
    hoomd.md.integrate.mode_standard(dt=0.005)
    hoomd.md.integrate.nvt(hoomd.group.all(), kT=1, tau=1)
    hoomd.run(1000)
    snap_final = square_lattice.take_snapshot()
    assert np.linalg.norm(snap_final.particles.position - snap_init.particles.position).mean() < 0.01

