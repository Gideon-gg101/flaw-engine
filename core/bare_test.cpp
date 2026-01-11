#include <pybind11/pybind11.h>
namespace py = pybind11;
PYBIND11_MODULE(bare_test, m) {
  m.def("hello", []() { return "Hello from C++!"; });
}
