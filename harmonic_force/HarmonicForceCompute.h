// Copyright (c) 2018 Malcolm Ramsay

// inclusion guard
#ifndef _HARMONIC_FORCE_COMPUTE_H_
#define _HARMONIC_FORCE_COMPUTE_H_

/*! \file HarmonicForceCompute.h
    \brief Declaration of HarmonicForceCompute
*/

#include <hoomd/ForceCompute.h>

// pybind11 is used to create the python bindings to the C++ object,
// but not if we are compiling GPU kernels
#ifndef NVCC
#include <hoomd/extern/pybind/include/pybind11/pybind11.h>
#endif

class HarmonicForceCompute : public ForceCompute {
 public:
  //! Constructor
  HarmonicForceCompute(std::shared_ptr<SystemDefinition> sysdef,
                       std::shared_ptr<ParticleGroup> group,
                       pybind11::list p_lst, pybind11::list o_lst,
                       Scalar translational_force_constant,
                       Scalar rotational_force_constant);

  //! Destructor
  ~HarmonicForceCompute();

 protected:
  //! Set the force to a new value
  virtual void setForces();

  //! Actually compute the forces
  virtual void computeForces(unsigned int timestep);

  std::shared_ptr<ParticleGroup>
      m_group;  //!< Group of particles on which this force is applied

  GPUArray<Scalar3> m_position_lattice;
  GPUArray<Scalar4> m_orientation_lattice;

  Scalar translational_force_constant;
  Scalar rotational_force_constant;

  unsigned int last_computed;
};

//! Exports the ActiveForceComputeClass to python
void export_HarmonicForceCompute(pybind11::module& m);

#endif  // _HARMONIC_FORCE_COMPUTE_H_
