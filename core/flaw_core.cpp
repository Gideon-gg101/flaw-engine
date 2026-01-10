#include "board.h"
#include "dis.h"
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

PYBIND11_MODULE(flaw_core, m) {
  py::class_<Move>(m, "Move")
      .def(py::init<int, int, Piece>())
      .def_readwrite("from_sq", &Move::from)
      .def_readwrite("to_sq", &Move::to)
      .def_readwrite("promotion", &Move::promotion);

  py::enum_<Piece>(m, "Piece")
      .value("EMPTY", EMPTY)
      .value("WP", WP)
      .value("WN", WN)
      .value("WB", WB)
      .value("WR", WR)
      .value("WQ", WQ)
      .value("WK", WK)
      .value("BP", BP)
      .value("BN", BN)
      .value("BB", BB)
      .value("BR", BR)
      .value("BQ", BQ)
      .value("BK", BK);

  py::enum_<Color>(m, "Color").value("WHITE", WHITE).value("BLACK", BLACK);

  py::class_<Board>(m, "Board")
      .def(py::init<>())
      .def(py::init<const Board &>()) // Copy constructor
      .def("load_fen", &Board::loadFEN)
      .def("to_fen", &Board::toFEN)
      .def("make_move", &Board::makeMove)
      .def("generate_moves", &Board::getPseudoLegalMoves)
      .def("is_game_over", &Board::isGameOver)
      .def("get_result", &Board::getResult)
      .def("piece_at", &Board::pieceAt)
      .def_readwrite("side_to_move", &Board::sideToMove);

  py::class_<IntentContext>(m, "IntentContext")
      .def(py::init<double, double, double, double, double>(),
           py::arg("c") = 1.0, py::arg("a") = 1.0, py::arg("d") = 1.0,
           py::arg("t") = 1.0, py::arg("r") = 1.0)
      .def_readwrite("control", &IntentContext::control)
      .def_readwrite("attack", &IntentContext::attack)
      .def_readwrite("defense", &IntentContext::defense)
      .def_readwrite("tempo", &IntentContext::tempo)
      .def_readwrite("risk", &IntentContext::risk);

  m.def("search", &DIS::search, "Run DIS search",
        py::call_guard<py::gil_scoped_release>());
  m.def("Evaluator_evaluate", &Evaluator::evaluate, "Run C++ evaluator");
}
