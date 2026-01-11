#ifndef DIS_H
#define DIS_H
#include "board.h"
#include "evaluator.h"
#include "movegen.h"
#include <vector>

#include "types.h"

namespace DIS {
int search(Board &b, int depth, int alpha, int beta, IntentContext ctx);
IntentContext updateIntent(const IntentContext &ctx, const Move &m,
                           const Board &b);
} // namespace DIS
#endif
