// Copyright (c) 2018 Malcolm Ramsay


#include "HarmonicForceCompute.h"

namespace py=pybind11;

/*! \file HarmonicForceCompute.cc
  \brief Definition of HarmonicForceCompute
  */

// ********************************
// here follows the code for HarmonicForce on the CPU

/*! \param sysdef System to zero the velocities of
*/
HarmonicForceCompute::HarmonicForceCompute(
        std::shared_ptr<SystemDefinition> sysdef,
        std::shared_ptr<ParticleGroup> group,
        py::list position_lattice,
        py::list orientation_lattice,
        Scalar force_constant
        ) : ForceCompute(sysdef), m_group(group), force_constant(force_constant)
{
    unsigned int group_size = m_group->getNumMembersGlobal();
    if (group_size == 0)
    {
        m_exec_conf->msg->error() << "Creating a HarmonicForce with an empty group" << std::endl;
        throw std::runtime_error("Error initializing HarmonicForce");
    }

    // Convert Python array types to C++ array types
    std::vector<Scalar3> c_position_lattice;
    py::tuple tmp_position;
    for (unsigned int i = 0; i < len(position_lattice); i++)
    {
        tmp_position = py::cast<py::tuple>(position_lattice[i]);
        if (len(tmp_position) != 3)
            throw std::runtime_error("Non-3D position given for HarmonicForceCompute");
        c_position_lattice.push_back( make_scalar3(py::cast<Scalar>(tmp_position[0]), py::cast<Scalar>(tmp_position[1]), py::cast<Scalar>(tmp_position[2])));
    }

    // Convert Python array types to C++ array types
    std::vector<Scalar4> c_orientation_lattice;
    py::tuple tmp_orientation;
    for (unsigned int i = 0; i < len(orientation_lattice); i++)
    {
        tmp_orientation = py::cast<py::tuple>(orientation_lattice[i]);
        if (len(tmp_orientation) != 4)
            throw std::runtime_error("Non-quaternion orientation given for HarmonicForceCompute");
        c_orientation_lattice.push_back( make_scalar4(py::cast<Scalar>(tmp_orientation[0]),
                    py::cast<Scalar>(tmp_orientation[1]),
                    py::cast<Scalar>(tmp_orientation[2]),
                    py::cast<Scalar>(tmp_orientation[3])
                    ));
    }


    // Check sizes are correct
    if (c_position_lattice.size() != group_size) { throw std::runtime_error("Positions given for HarmonicForceCompute doesn't match particle number."); }
    if (c_orientation_lattice.size() != group_size) { throw std::runtime_error("Orientation given for HarmonicForceCompute doesn't match particle number."); }


    // Create the arrays
    GPUArray<Scalar3> tmp_position_lattice(group_size, m_exec_conf);
    GPUArray<Scalar4> tmp_orientation_lattice(group_size, m_exec_conf);

    // Link the class value to the initialised arrays
    m_position_lattice.swap(tmp_position_lattice);
    m_orientation_lattice.swap(tmp_orientation_lattice);

    // Create the handles for modifying the arrays
    ArrayHandle<Scalar3> h_position_lattice(m_position_lattice, access_location::host);
    ArrayHandle<Scalar4> h_orientation_lattice(m_orientation_lattice, access_location::host);

    // Assign values to arrays
    for (unsigned int i = 0; i < group_size; i++)
    {
        h_position_lattice.data[i] = make_scalar3(0, 0, 0);
        h_position_lattice.data[i].x = c_position_lattice[i].x;
        h_position_lattice.data[i].y = c_position_lattice[i].y;
        h_position_lattice.data[i].z = c_position_lattice[i].z;

        h_orientation_lattice.data[i] = make_scalar4(0, 0, 0, 0);
        h_orientation_lattice.data[i].x = c_orientation_lattice[i].x;
        h_orientation_lattice.data[i].y = c_orientation_lattice[i].y;
        h_orientation_lattice.data[i].z = c_orientation_lattice[i].z;
        h_orientation_lattice.data[i].w = c_orientation_lattice[i].w;
    }

    last_computed = 10;

    // broadcast the seed from rank 0 to all other ranks.
#ifdef ENABLE_MPI
    if(this->m_pdata->getDomainDecomposition())
        bcast(m_seed, 0, this->m_exec_conf->getMPICommunicator());
#endif
}

HarmonicForceCompute::~HarmonicForceCompute()
    {
    m_exec_conf->msg->notice(5) << "Destroying HarmonincForceCompute" << std::endl;
    }

void HarmonicForceCompute::setForces()
{
    // Create array handles
    ArrayHandle<Scalar3> h_position_lattice(m_position_lattice, access_location::host, access_mode::read);
    ArrayHandle<Scalar4> h_orientation_lattice(m_orientation_lattice, access_location::host, access_mode::read);

    ArrayHandle<Scalar4> h_force(m_force,access_location::host,access_mode::overwrite);
    ArrayHandle<Scalar4> h_torque(m_torque,access_location::host,access_mode::overwrite);

    ArrayHandle<Scalar4> h_position(m_pdata->getPositions(), access_location::host, access_mode::readwrite);
    ArrayHandle<Scalar4> h_orientation(m_pdata->getOrientationArray(), access_location::host, access_mode::readwrite);

    ArrayHandle<unsigned int> h_rtag(m_pdata->getRTags(), access_location::host, access_mode::read);

    // sanity check
    assert(h_position_lattice.data != NULL);
    assert(h_orientation_lattice.data != NULL);
    assert(h_force.data != NULL);
    assert(h_torque.data != NULL);
    assert(h_position.data != NULL);
    assert(h_orientation.data != NULL);

    // zero forces so we don't leave any forces set for indices that are no longer part of our group
    memset(h_force.data, 0, sizeof(Scalar4) * m_force.getNumElements());
    memset(h_torque.data, 0, sizeof(Scalar4) * m_force.getNumElements());

    // Iterate through all group members
    for (unsigned int i = 0; i < m_group->getNumMembers(); i++)
    {
        unsigned int tag = m_group->getMemberTag(i);
        unsigned int idx = h_rtag.data[tag];

        quat<Scalar> q0(h_orientation_lattice.data[i]);
        quat<Scalar> dq = q0 - quat<Scalar>(h_orientation.data[idx]);
        Scalar norm_dq = norm2(dq);
        Scalar4 d_rot = quat_to_scalar4(dq);

        int3 dummy = make_int3(0,0,0);
        vec3<Scalar> origin(m_pdata->getOrigin());
        vec3<Scalar> position(h_position.data[idx]);
        const BoxDim& box = this->m_pdata->getGlobalBox();
        vec3<Scalar> r0(h_position_lattice.data[idx]);
        Scalar3 t = vec_to_scalar3(position - origin);
        box.wrap(t, dummy);
        vec3<Scalar> shifted_pos(t);
        vec3<Scalar> dr = vec3<Scalar>(box.minImage(vec_to_scalar3(r0 - position + origin)));

        h_force.data[idx].x = -force_constant * dr.x;
        h_force.data[idx].y = -force_constant * dr.y;
        h_force.data[idx].z = -force_constant * dr.z;

        h_torque.data[idx].x = -force_constant * norm_dq * d_rot.x;
        h_torque.data[idx].y = -force_constant * norm_dq * d_rot.y;
        h_torque.data[idx].z = -force_constant * norm_dq * d_rot.z;

    }
}


/*! Perform the needed calculations to zero the system's velocity
  \param timestep Current time step of the simulation
  */
void HarmonicForceCompute::computeForces(unsigned int timestep)
{
    if (m_prof) m_prof->push(m_exec_conf,  "HarmonicForceCompute");

    if (last_computed != timestep)
    {
        last_computed = timestep;

        setForces();
    }

    if (m_prof) m_prof->pop();
}

/* Export the CPU updater to be visible in the python module
*/
void export_HarmonicForceCompute(py::module& m)
{
    py::class_< HarmonicForceCompute, std::shared_ptr<HarmonicForceCompute> >(m, "HarmonicForceCompute", py::base<ForceCompute>())
        .def(py::init< std::shared_ptr<SystemDefinition>, std::shared_ptr<ParticleGroup>, py::list, py::list, Scalar >())
        ;
}
