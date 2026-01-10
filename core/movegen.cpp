#include "movegen.h"
namespace MoveGen {
std::vector<Move> generateLegalMoves(const Board &b) {
  std::vector<Move> pseudo = b.getPseudoLegalMoves();
  std::vector<Move> legal;
  for (auto &m : pseudo) {
    Board copy = b;
    copy.makeMove(m);
    // Warning: simplified check test (always checks square 0 for attacks)
    // This is from user snippet, preserving as requested.
    bool inCheck = copy.isSquareAttacked(0, (Color)!b.sideToMove);
    if (!inCheck)
      legal.push_back(m);
  }
  return legal;
}
} // namespace MoveGen
