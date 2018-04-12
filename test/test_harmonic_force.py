#! /usr/bin/env python3
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
        yield hoomd.init.create_lattice(unitcell=hoomd.lattice.sq(a=2.0), n=5)


@pytest.fixture
def simulation_setup():
    delta = 0
    create_rigid = False
    with hoomd.context.initialize():
        unit_cell = hoomd.lattice.unitcell(
            N=1,
            a1=[2, 0, 0],
            a2=[0, 2, 0],
            a3=[0, 0, 1],
            dimensions=2,
            position=[[delta, delta, 0]],
            type_name=['A'],
            mass=[1.0],
            moment_inertia=[[0, 0, 1]],
            orientation=[[1 - delta, 0, 0, delta]],
        )
        system = hoomd.init.create_lattice(unitcell=unit_cell, n=5)
        pairs = hoomd.md.pair.lj(2.5, nlist=hoomd.md.nlist.cell())
        pairs.pair_coeff.set('A', 'A', epsilon=1.0, sigma=1.0)
        group = hoomd.group.all()
        nmols = system.particles.get_metadata()['N']
        if create_rigid:
            system.particles.types.add('B')
            pairs.pair_coeff.set('A', 'B', epsilon=1.0, sigma=1.0)
            pairs.pair_coeff.set('B', 'B', epsilon=1.0, sigma=1.0)
            rigid = hoomd.md.constrain.rigid()
            rigid.set_param('A', types=['B'], positions=[(-1, 0, 0)])
            rigid.create_bodies()
            group = hoomd.group.rigid_center()
        hoomd.md.update.enforce2d()
        hoomd.md.integrate.mode_standard(dt=0.005)
        hoomd.md.integrate.nvt(group, kT=1, tau=1)
        yield {'system': system, 'group': group, 'nmols': nmols, 'delta': delta}


def test_simple(square_lattice):
    snap = square_lattice.take_snapshot()
    HarmonicForceCompute(
        hoomd.group.all(),
        [tuple(row) for row in snap.particles.position],
        [tuple(row) for row in snap.particles.orientation],
        1.,
    )
    hoomd.run(10)


def test_no_diffusion(square_lattice):
    snap_init = square_lattice.take_snapshot()
    pairs = hoomd.md.pair.lj(2.5, nlist=hoomd.md.nlist.cell())
    pairs.pair_coeff.set("A", "A", epsilon=1.0, sigma=1.0)
    HarmonicForceCompute(
        hoomd.group.all(),
        [tuple(row) for row in snap_init.particles.position],
        [tuple(row) for row in snap_init.particles.orientation],
        1.,
    )
    hoomd.md.update.enforce2d()
    hoomd.md.integrate.mode_standard(dt=0.005)
    hoomd.md.integrate.nvt(hoomd.group.all(), kT=1, tau=1)
    hoomd.run(1000)
    snap_final = square_lattice.take_snapshot()
    assert np.linalg.norm(
        snap_final.particles.position - snap_init.particles.position
    ).mean() < 0.01

def test_no_rotation(simulation_setup):
    snap_init = simulation_setup['system'].take_snapshot()
    nmols = simulation_setup['nmols']
    group = simulation_setup['group']
    HarmonicForceCompute(group,
                         snap_init.particles.position[:nmols],
                         snap_init.particles.orientation[:nmols],
                         10.
                         )
    hoomd.run(1000)
    snap_final = simulation_setup['system'].take_snapshot()
    assert np.linalg.norm(
        snap_final.particles.orientation - snap_init.particles.orientation
    ).mean() < 0.01
