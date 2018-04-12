#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Malcolm Ramsay <malramsay64@gmail.com>
#
# Distributed under terms of the MIT license.

"""Test appplying the harmonic force to a simulation."""

import itertools

import hoomd
import numpy as np
import pytest
from hoomd.harmonic_force import HarmonicForceCompute


@pytest.fixture(params=itertools.product([-0.1, 0, 0.1, 0.4], [True, False]))
def simulation_setup(delta: float = 0, create_rigid: bool = False):
    with hoomd.context.initialize(""):
        unit_cell = hoomd.lattice.unitcell(
            N=1,
            a1=[2, 0, 0],
            a2=[0, 2, 0],
            a3=[0, 0, 1],
            dimensions=2,
            position=[[delta, delta, 0]],
            type_name=["A"],
            mass=[1.0],
            moment_inertia=[[0, 0, 1]],
            orientation=[[1 - delta, 0, 0, delta]],
        )
        system = hoomd.init.create_lattice(unitcell=unit_cell, n=5)
        pairs = hoomd.md.pair.lj(2.5, nlist=hoomd.md.nlist.cell())
        pairs.pair_coeff.set("A", "A", epsilon=1.0, sigma=1.0)
        group = hoomd.group.all()
        nmols = system.particles.get_metadata()["N"]
        if create_rigid:
            system.particles.types.add("B")
            pairs.pair_coeff.set("A", "B", epsilon=1.0, sigma=1.0)
            pairs.pair_coeff.set("B", "B", epsilon=1.0, sigma=1.0)
            rigid = hoomd.md.constrain.rigid()
            rigid.set_param("A", types=["B"], positions=[(-1, 0, 0)])
            rigid.create_bodies()
            group = hoomd.group.rigid_center()
        hoomd.md.update.enforce2d()
        hoomd.md.integrate.mode_standard(dt=0.005)
        hoomd.md.integrate.nvt(group, kT=1, tau=1)
        yield {"system": system, "group": group, "nmols": nmols, "delta": delta}


def test_HarmonicForceCompute(simulation_setup):
    snap_init = simulation_setup["system"].take_snapshot()
    nmols = simulation_setup["nmols"]
    group = simulation_setup["group"]
    delta = simulation_setup["delta"]
    intended_position = snap_init.particles.position[:nmols] - np.array(
        [delta, delta, 0]
    )
    intended_orientation = snap_init.particles.orientation[:nmols] - np.array(
        [-delta, 0, 0, delta]
    )
    HarmonicForceCompute(group, intended_position, intended_orientation, 10., 10.)
    hoomd.run(1000)
    snap_final = simulation_setup["system"].take_snapshot()
    assert np.all(
        np.linalg.norm(snap_final.particles.position[:nmols] - intended_position) < 0.01
    )
    assert np.all(
        np.linalg.norm(snap_final.particles.orientation[:nmols] - intended_orientation)
        < 0.01
    )
