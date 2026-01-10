#ifndef BOARD_H
#define BOARD_H
#include <cstdint>
#include <string>
#include <vector>

enum Piece { EMPTY, WP, WN, WB, WR, WQ, WK, BP, BN, BB, BR, BQ, BK };
enum Color { WHITE, BLACK };

struct Move {
  int from, to;
  Piece promotion;
  Move(int f = 0, int t = 0, Piece p = EMPTY) : from(f), to(t), promotion(p) {}
};

class Board {
public:
  uint64_t zobristKey;
  static uint64_t zobristTable[13][64];
  static uint64_t sideKey;
  static bool zobristInitialized;
  static void initZobrist();
  uint64_t hash() const { return zobristKey; }
  void recalculateHash();

  uint64_t bitboards[13];
  Color sideToMove;
  uint8_t castlingRights;
  int enPassant;
  Board();
  void loadFEN(const std::string &fen);
  std::string toFEN() const;
  void makeMove(const Move &m);
  std::vector<Move> getPseudoLegalMoves() const;
  Piece pieceAt(int square) const;
  bool isSquareAttacked(int square, Color by) const;
  bool isGameOver() const;
  int getResult() const; // 1: White win, -1: Black win, 0: Draw/Ongoing

private:
  void clear();
};
#endif