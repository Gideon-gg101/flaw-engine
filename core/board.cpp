#include "board.h"
#include <cctype>
#include <iostream>
#include <sstream>

uint64_t Board::zobristTable[13][64];
uint64_t Board::sideKey;
bool Board::zobristInitialized = false;

void Board::initZobrist() {
  if (zobristInitialized)
    return;
  uint64_t seed = 123456789;
  auto rand64 = [&]() {
    seed ^= seed >> 12;
    seed ^= seed << 25;
    seed ^= seed >> 27;
    return seed * 2685821657736338717ULL;
  };
  for (int p = 0; p < 13; ++p)
    for (int s = 0; s < 64; ++s)
      zobristTable[p][s] = rand64();
  sideKey = rand64();
  zobristInitialized = true;
}

Board::Board() {
  initZobrist();
  clear();
  sideToMove = WHITE;
  castlingRights = 0;
  enPassant = -1;
}
void Board::clear() {
  for (int i = 0; i < 13; ++i)
    bitboards[i] = 0ULL;
}
static int squareIndex(int rank, int file) { return rank * 8 + file; }
void Board::loadFEN(const std::string &fen) {
  clear();
  std::istringstream ss(fen);
  std::string boardPart;
  ss >> boardPart;
  int rank = 7, file = 0;
  for (char c : boardPart) {
    if (c == '/') {
      rank--;
      file = 0;
      continue;
    }
    if (std::isdigit(c)) {
      file += c - '0';
      continue;
    }
    Piece p = EMPTY;
    bool isWhite = std::isupper(c);
    switch (std::tolower(c)) {
    case 'p':
      p = isWhite ? WP : BP;
      break;
    case 'n':
      p = isWhite ? WN : BN;
      break;
    case 'b':
      p = isWhite ? WB : BB;
      break;
    case 'r':
      p = isWhite ? WR : BR;
      break;
    case 'q':
      p = isWhite ? WQ : BQ;
      break;
    case 'k':
      p = isWhite ? WK : BK;
      break;
    }
    bitboards[p] |= (1ULL << squareIndex(rank, file));
    file++;
  }
  std::string stm;
  ss >> stm;
  sideToMove = (stm == "w") ? WHITE : BLACK;
  recalculateHash();
}

void Board::recalculateHash() {
  zobristKey = 0;
  for (int sq = 0; sq < 64; ++sq) {
    Piece p = pieceAt(sq);
    if (p != EMPTY)
      zobristKey ^= zobristTable[p][sq];
  }
  if (sideToMove == BLACK)
    zobristKey ^= sideKey;
}
Piece Board::pieceAt(int square) const {
  for (int p = WP; p <= BK; ++p)
    if (bitboards[p] & (1ULL << square))
      return static_cast<Piece>(p);
  return EMPTY;
}
void Board::makeMove(const Move &m) {
  Piece moving = pieceAt(m.from);
  Piece captured = EMPTY;
  // Identify captured piece
  for (int p = 1; p <= 12; ++p) { // 1 to 12 (WP=1 .. BK=12) assuming EMPTY=0
    if (bitboards[p] & (1ULL << m.to)) {
      captured = static_cast<Piece>(p);
      break;
    }
  }

  // Hash update: remove moving and captured
  zobristKey ^= zobristTable[moving][m.from];
  if (captured != EMPTY)
    zobristKey ^= zobristTable[captured][m.to];

  // Bitboard updates
  for (int i = 0; i < 12; ++i)
    bitboards[i] &= ~(1ULL << m.to);
  bitboards[moving] &= ~(1ULL << m.from);
  bitboards[moving] |= (1ULL << m.to);

  // Hash update: add moving at new square
  zobristKey ^= zobristTable[moving][m.to];

  // Side update
  sideToMove = (sideToMove == WHITE) ? BLACK : WHITE;
  zobristKey ^= sideKey;
}

std::string Board::toFEN() const {
  std::string fen = "";
  for (int rank = 7; rank >= 0; rank--) {
    int emptyCount = 0;
    for (int file = 0; file < 8; file++) {
      Piece p = pieceAt(squareIndex(rank, file));
      if (p == EMPTY) {
        emptyCount++;
      } else {
        if (emptyCount > 0) {
          fen += std::to_string(emptyCount);
          emptyCount = 0;
        }
        static const char pieceChars[] = " PNBRQKpnbrqk";
        fen += pieceChars[p];
      }
    }
    if (emptyCount > 0)
      fen += std::to_string(emptyCount);
    if (rank > 0)
      fen += "/";
  }
  fen += (sideToMove == WHITE) ? " w " : " b ";
  fen += "- - 0 1"; // Simplified placeholders
  return fen;
}

bool Board::isGameOver() const {
  return getPseudoLegalMoves().empty(); // Basic check for mate/stalemate
}

int Board::getResult() const {
  if (!isGameOver())
    return 0;
  // If sideToMove king is attacked, it's mate -> they lost
  // Finding king square
  int kingSq = -1;
  Piece k = (sideToMove == WHITE) ? WK : BK;
  uint64_t bb = bitboards[k];
  if (bb) {
#if defined(_MSC_VER) && !defined(__clang__)
    unsigned long idx;
    _BitScanForward64(&idx, bb);
    kingSq = idx;
#else
    kingSq = __builtin_ctzll(bb);
#endif
  }
  if (kingSq != -1 &&
      isSquareAttacked(kingSq, (sideToMove == WHITE) ? BLACK : WHITE)) {
    return (sideToMove == WHITE) ? -1 : 1;
  }
  return 0; // Stalemate
}
bool Board::isSquareAttacked(int square, Color by) const {
  // simplified attack detection (knights + pawns)
  static const int knightOffsets[8] = {17, 15, 10, 6, -17, -15, -10, -6};
  for (int o : knightOffsets) {
    int sq = square + o;
    if (sq < 0 || sq > 63)
      continue;
    Piece attacker = (by == WHITE) ? WN : BN;
    if (bitboards[attacker] & (1ULL << sq))
      return true;
  }
  // basic pawn attack check
  int dir = (by == WHITE) ? -8 : 8;
  int left = (square + dir - 1), right = (square + dir + 1);
  Piece pawn = (by == WHITE) ? WP : BP;
  if (left >= 0 && left < 64 && (bitboards[pawn] & (1ULL << left)))
    return true;
  if (right >= 0 && right < 64 && (bitboards[pawn] & (1ULL << right)))
    return true;
  return false;
}
std::vector<Move> Board::getPseudoLegalMoves() const {
  std::vector<Move> moves;
  uint64_t bb = (sideToMove == WHITE) ? bitboards[WP] : bitboards[BP];
  int dir = (sideToMove == WHITE) ? 8 : -8;
  while (bb) {
// Basic builtin wrapper or fallback
#if defined(_MSC_VER) && !defined(__clang__)
    unsigned long index;
    _BitScanForward64(&index, bb);
    int from = index;
#else
    int from = __builtin_ctzll(bb);
#endif
    int to = from + dir;
    if (to >= 0 && to < 64)
      moves.push_back(Move(from, to));
    bb &= bb - 1;
  }
  return moves;
}
