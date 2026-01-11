#ifndef EVALUATOR_H
#define EVALUATOR_H
#include "board.h"

// Forward declaration if needed, or just include the header if DIS is needed.
// Since IntentContext is in dis.h, we should include it or move IntentContext.
#include "types.h"

namespace Evaluator {
int evaluate(const Board &b, const IntentContext &ctx);
}
#endif
