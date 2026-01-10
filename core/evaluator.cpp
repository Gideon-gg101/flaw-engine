#include "evaluator.h"
static const int pieceValue[13] = {0,    100,  320,  330,  500,  900,   20000,
                                   -100, -320, -330, -500, -900, -20000};
// WP, WN, WB, WR, WQ, WK, BP, BN, BB, BR, BQ, BK
// Note: enum Piece defines EMPTY=0, so this array might be off by one if
// accessed directly by enum value without offset or if enum order matches.
// Piece enum: EMPTY=0, WP=1 ... BK=12.
// Array indices: 0..12.
// pieceValue[EMPTY] = 0. pieceValue[WP] = 100. Looks correct.

int Evaluator::evaluate(const Board &b) {
  int score = 0;
  for (int p = WP; p <= BK; ++p) {
    uint64_t bb = b.bitboards[p];
    while (bb) {
      bb &= bb - 1;
      score += pieceValue[p];
    }
  }
  return (b.sideToMove == WHITE) ? score : -score;
}
