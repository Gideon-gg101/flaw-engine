#include "evaluator.h"
static const int pieceValue[13] = {0,    100,  320,  330,  500,  900,   20000,
                                   -100, -320, -330, -500, -900, -20000};
// WP, WN, WB, WR, WQ, WK, BP, BN, BB, BR, BQ, BK
// Note: enum Piece defines EMPTY=0, so this array might be off by one if
// accessed directly by enum value without offset or if enum order matches.
// Piece enum: EMPTY=0, WP=1 ... BK=12.
// Array indices: 0..12.
// pieceValue[EMPTY] = 0. pieceValue[WP] = 100. Looks correct.

int Evaluator::evaluate(const Board &b, const IntentContext &ctx) {
  int score = 0;

  // Use intent weights to scale material value
  // own_weight = ctx.defense roughly
  // enemy_weight = ctx.attack roughly

  for (int p = WP; p <= BK; ++p) {
    uint64_t bb = b.bitboards[p];
    int count = 0;
    while (bb) {
      bb &= bb - 1;
      count++;
    }

    int val = pieceValue[p];

    // Scale based on intent
    if (b.sideToMove == WHITE) {
      if (p >= WP && p <= WK) {
        // Own pieces
        score += val * ctx.defense;
      } else {
        // Enemy pieces
        score += val * ctx.attack;
      }
    } else {
      if (p >= BP && p <= BK) {
        // Own pieces
        score += val * ctx.defense;
      } else {
        // Enemy pieces
        score += val * ctx.attack;
      }
    }
  }
  return score;
}
