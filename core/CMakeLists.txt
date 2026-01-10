cmake_minimum_required(VERSION 3.14)
project(flaw_core)
set(CMAKE_CXX_STANDARD 17)

include(FetchContent)
FetchContent_Declare(
  pybind11
  GIT_REPOSITORY https://github.com/pybind/pybind11
  GIT_TAG        v2.11.1
)
FetchContent_MakeAvailable(pybind11)

pybind11_add_module(flaw_core
    flaw_core.cpp
    board.cpp 
    movegen.cpp 
    evaluator.cpp 
    dis.cpp
)
