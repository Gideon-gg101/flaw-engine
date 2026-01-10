#ifndef DIS_H
#define DIS_H
#include "board.h"
#include "evaluator.h"
#include "movegen.h"
#include <vector>

struct IntentContext {
  double control, attack, defense, tempo, risk;
  IntentContext(double c = 1, double a = 1, double d = 1, double t = 1,
                double r = 1)
      : control(c), attack(a), defense(d), tempo(t), risk(r) {}
};

namespace DIS {
int search(Board &b, int depth, int alpha, int beta, IntentContext ctx);
IntentContext updateIntent(const IntentContext &ctx, const Move &m,
                           const Board &b);
} // namespace DIS
#endif
