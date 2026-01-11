#include "board.h"
#include "dis.h"
#include "evaluator.h"
#include <iostream>


int main() {
  std::cout << "Starting Test..." << std::endl;
  Board b;
  b.loadFEN("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");
  std::cout << "Board Loaded." << std::endl;

  IntentContext ctx;
  int score = Evaluator::evaluate(b, ctx);
  std::cout << "Initial Evaluation: " << score << std::endl;

  std::vector<Move> moves = b.getPseudoLegalMoves();
  std::cout << "Found " << moves.size() << " initial moves." << std::endl;

  for (auto &m : moves) {
    std::cout << "Move: " << m.from << " -> " << m.to << std::endl;
  }

  std::cout << "Test Complete." << std::endl;
  return 0;
}
