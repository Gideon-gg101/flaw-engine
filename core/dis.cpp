#include "dis.h"
#include "transposition.h"
#include <algorithm>
#include <cmath>

using namespace DIS;

TranspositionTable tt;

IntentContext DIS::updateIntent(const IntentContext &ctx, const Move &m,
                                const Board &b) {
  // Update based on move characteristics (simplified heuristics)
  IntentContext n = ctx;
  Piece p = b.pieceAt(m.from);
  if (p == WP || p == BP)
    n.tempo += 0.1;
  if (p == WQ || p == BQ)
    n.attack += 0.2;
  if (p == WK || p == BK)
    n.defense += 0.3;
  n.risk = std::max(0.5, ctx.risk * 0.95);
  return n;
}

int DIS::search(Board &b, int depth, int alpha, int beta, IntentContext ctx) {
  TTEntry entry;
  if (tt.probe(b.hash(), entry) && entry.depth >= depth)
    return entry.score;

  if (depth == 0)
    return Evaluator::evaluate(b, ctx);
  std::vector<Move> moves = MoveGen::generateLegalMoves(b);
  if (moves.empty())
    return Evaluator::evaluate(b, ctx);

  // MVV-LVA Move Ordering
  std::sort(moves.begin(), moves.end(), [&](const Move &a, const Move &b2) {
    Piece victimA = b.pieceAt(a.to);
    Piece victimB = b.pieceAt(b2.to);
    Piece attackerA = b.pieceAt(a.from);
    Piece attackerB = b.pieceAt(b2.from);

    // Simple material values for sorting
    static const int mvvValue[13] = {0,  10, 20, 20, 40, 80, 100,
                                     10, 20, 20, 40, 80, 100};

    int scoreA = 0;
    if (victimA != EMPTY)
      scoreA = (mvvValue[victimA] * 10) - (mvvValue[attackerA] / 10);

    int scoreB = 0;
    if (victimB != EMPTY)
      scoreB = (mvvValue[victimB] * 10) - (mvvValue[attackerB] / 10);

    // Context weight influence
    if (attackerA == WK || attackerA == BK)
      scoreA -= ctx.risk * 10;
    if (attackerB == WK || attackerB == BK)
      scoreB -= ctx.risk * 10;

    return scoreA > scoreB;
  });

  for (auto &m : moves) {
    Board copy = b;
    copy.makeMove(m);
    IntentContext newCtx = updateIntent(ctx, m, b);
    int score = -search(copy, depth - 1, -beta, -alpha, newCtx);
    if (score >= beta) {
      tt.store(b.hash(), beta, depth);
      return beta;
    }
    if (score > alpha)
      alpha = score;
  }
  tt.store(b.hash(), alpha, depth);
  return alpha;
}
