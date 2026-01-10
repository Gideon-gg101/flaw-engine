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
    return Evaluator::evaluate(b);
  std::vector<Move> moves = MoveGen::generateLegalMoves(b);
  if (moves.empty())
    return Evaluator::evaluate(b);

  // Intent-weighted move sorting (rough heuristic)
  std::sort(moves.begin(), moves.end(), [&](const Move &a, const Move &b2) {
    return (a.to % 8 + ctx.attack * 2) > (b2.to % 8 + ctx.defense);
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
