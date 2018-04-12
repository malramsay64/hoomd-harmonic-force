// Copyright (c) 2018 Malcolm Ramsay

// Include the defined classes that are to be exported to python
#include "HarmonicForceCompute.h"

#include <hoomd/extern/pybind/include/pybind11/pybind11.h>

// specify the python module. Note that the name must expliclty match the
// PROJECT() name provided in CMakeLists (with an underscore in front)
PYBIND11_PLUGIN(_harmonic_force) {
  pybind11::module m("_harmonic_force");
  export_HarmonicForceCompute(m);

  return m.ptr();
}
