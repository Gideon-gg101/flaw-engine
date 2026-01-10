#include "board.h"
#include "dis.h"
#include "evaluator.h"
#include "movegen.h"
#include <iostream>


int main() {
  Board b;
  b.loadFEN("8/8/8/8/8/8/8/8 w - - 0 1"); // empty board placeholder
  std::cout << "Flaw Engine Core Test\n";
  b.loadFEN("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");
  std::vector<Move> moves = MoveGen::generateLegalMoves(b);
  std::cout << "Legal moves: " << moves.size() << "\n";
  IntentContext ctx;
  int eval = DIS::search(b, 2, -10000, 10000, ctx);
  std::cout << "Search score: " << eval << "\n";
  return 0;
}
