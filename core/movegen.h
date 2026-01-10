#ifndef MOVEGEN_H
#define MOVEGEN_H
#include "board.h"
#include <vector>
namespace MoveGen {
std::vector<Move> generateLegalMoves(const Board &b);
}
#endif
