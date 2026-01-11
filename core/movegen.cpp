#include "movegen.h"
namespace MoveGen {
std::vector<Move> generateLegalMoves(const Board &b) {
  std::vector<Move> pseudo = b.getPseudoLegalMoves();
  std::vector<Move> legal;
  for (auto &m : pseudo) {
    Board copy = b;
    copy.makeMove(m);
    // Find king square
    int kingSq = -1;
    Piece k = (b.sideToMove == WHITE) ? WK : BK;
    uint64_t bb = copy.bitboards[k];
    if (bb) {
#if defined(_MSC_VER) && !defined(__clang__)
      unsigned long index;
      _BitScanForward64(&index, bb);
      kingSq = index;
#else
      kingSq = __builtin_ctzll(bb);
#endif
    }

    bool inCheck =
        (kingSq != -1) &&
        copy.isSquareAttacked(kingSq, (b.sideToMove == WHITE ? BLACK : WHITE));
    if (!inCheck)
      legal.push_back(m);
  }
  return legal;
}
} // namespace MoveGen
