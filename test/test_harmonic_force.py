#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Malcolm Ramsay <malramsay64@gmail.com>
#
# Distributed under terms of the MIT license.

"""Test appplying the harmonic force to a simulation."""

import hoomd
import pytest
from hoomd.harmonic_force import HarmonicForceCompute

hoomd.context.initialize()

@pytest.fixture
def square_lattice():
    return hoomd.init.create_lattice(
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
