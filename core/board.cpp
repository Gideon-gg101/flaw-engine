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
  Piece target = pieceAt(m.to);

  // 1. Handle En Passant Capture
  if ((moving == WP || moving == BP) && m.to == enPassant) {
    int capSq = (moving == WP) ? m.to - 8 : m.to + 8;
    Piece capPawn = pieceAt(capSq);
    zobristKey ^= zobristTable[capPawn][capSq];
    bitboards[capPawn] &= ~(1ULL << capSq);
  }

  // 2. Clear target square (Standard capture)
  if (target != EMPTY) {
    zobristKey ^= zobristTable[target][m.to];
    bitboards[target] &= ~(1ULL << m.to);
  }

  // 3. Handle Castling (Move the Rook)
  if (moving == WK && std::abs(m.to - m.from) == 2) {
    if (m.to == 6) { // White King Side
      bitboards[WR] &= ~(1ULL << 7);
      bitboards[WR] |= (1ULL << 5);
      zobristKey ^= zobristTable[WR][7] ^ zobristTable[WR][5];
    } else if (m.to == 2) { // White Queen Side
      bitboards[WR] &= ~(1ULL << 0);
      bitboards[WR] |= (1ULL << 3);
      zobristKey ^= zobristTable[WR][0] ^ zobristTable[WR][3];
    }
  } else if (moving == BK && std::abs(m.to - m.from) == 2) {
    if (m.to == 62) { // Black King Side
      bitboards[BR] &= ~(1ULL << 63);
      bitboards[BR] |= (1ULL << 61);
      zobristKey ^= zobristTable[BR][63] ^ zobristTable[BR][61];
    } else if (m.to == 58) { // Black Queen Side
      bitboards[BR] &= ~(1ULL << 56);
      bitboards[BR] |= (1ULL << 59);
      zobristKey ^= zobristTable[BR][56] ^ zobristTable[BR][59];
    }
  }

  // 4. Update Bitboards and Hash for moving piece
  zobristKey ^= zobristTable[moving][m.from];
  bitboards[moving] &= ~(1ULL << m.from);

  if (m.promotion != EMPTY) {
    bitboards[m.promotion] |= (1ULL << m.to);
    zobristKey ^= zobristTable[m.promotion][m.to];
  } else {
    bitboards[moving] |= (1ULL << m.to);
    zobristKey ^= zobristTable[moving][m.to];
  }

  // 5. Update Status: En Passant Square
  enPassant = -1;
  if (moving == WP && (m.to - m.from == 16))
    enPassant = m.from + 8;
  if (moving == BP && (m.from - m.to == 16))
    enPassant = m.from - 8;

  // 6. Update Status: Castling Rights
  if (moving == WK)
    castlingRights &= ~3;
  if (moving == BK)
    castlingRights &= ~12;
  if (m.from == 0 || m.to == 0)
    castlingRights &= ~2; // White Queen Rook
  if (m.from == 7 || m.to == 7)
    castlingRights &= ~1; // White King Rook
  if (m.from == 56 || m.to == 56)
    castlingRights &= ~8; // Black Queen Rook
  if (m.from == 63 || m.to == 63)
    castlingRights &= ~4; // Black King Rook

  // 7. Side and Key update
  sideToMove = (sideToMove == WHITE) ? BLACK : WHITE;
  zobristKey ^= sideKey;
  // Note: castling and ep hashes should ideally be toggled but omitted for
  // simplicity in this proto scope
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
  Color us = (by == WHITE) ? BLACK : WHITE;

  // Directions
  static const int knightDirs[8] = {17, 15, 10, 6, -17, -15, -10, -6};
  static const int rookDirs[4] = {8, -8, 1, -1};
  static const int bishopDirs[4] = {9, 7, -9, -7};
  static const int queenDirs[8] = {8, -8, 1, -1, 9, 7, -9, -7};

  // 1. Knights
  for (int d : knightDirs) {
    int to = square + d;
    if (to >= 0 && to < 64 && std::abs((to % 8) - (square % 8)) <= 2) {
      Piece p = (by == WHITE) ? WN : BN;
      if (bitboards[p] & (1ULL << to))
        return true;
    }
  }

  // 2. Pawns
  int pawnDir = (by == WHITE) ? -8 : 8;
  for (int side : {-1, 1}) {
    int to = square + pawnDir + side;
    if (to >= 0 && to < 64 && std::abs((to % 8) - (square % 8)) == 1) {
      Piece p = (by == WHITE) ? WP : BP;
      if (bitboards[p] & (1ULL << to))
        return true;
    }
  }

  // 3. King
  for (int d : queenDirs) {
    int to = square + d;
    if (to >= 0 && to < 64 && std::abs((to % 8) - (square % 8)) <= 1) {
      Piece p = (by == WHITE) ? WK : BK;
      if (bitboards[p] & (1ULL << to))
        return true;
    }
  }

  // 4. Sliders (Rooks, Bishops, Queens)
  auto checkSlider = [&](const int *dirs, int numDirs, Piece p1, Piece p2) {
    for (int i = 0; i < numDirs; ++i) {
      int to = square;
      while (true) {
        int nextTo = to + dirs[i];
        if (nextTo < 0 || nextTo >= 64)
          break;
        if (std::abs((nextTo % 8) - (to % 8)) > 2)
          break; // Wrapped board

        Piece found = pieceAt(nextTo);
        if (found != EMPTY) {
          if (found == p1 || found == p2)
            return true;
          break; // Blocked
        }
        to = nextTo;
      }
    }
    return false;
  };

  if (checkSlider(rookDirs, 4, (by == WHITE ? WR : BR),
                  (by == WHITE ? WQ : BQ)))
    return true;
  if (checkSlider(bishopDirs, 4, (by == WHITE ? WB : BB),
                  (by == WHITE ? WQ : BQ)))
    return true;

  return false;
}
std::vector<Move> Board::getPseudoLegalMoves() const {
  std::vector<Move> moves;
  Color us = sideToMove;
  Color them = (us == WHITE) ? BLACK : WHITE;

  // Directions for sliding pieces
  static const int rookDirs[4] = {8, -8, 1, -1};
  static const int bishopDirs[4] = {9, 7, -9, -7};
  static const int queenDirs[8] = {8, -8, 1, -1, 9, 7, -9, -7};
  static const int knightDirs[8] = {17, 15, 10, 6, -17, -15, -10, -6};

  for (int p_val = WP; p_val <= BK; ++p_val) {
    Piece p = static_cast<Piece>(p_val);
    bool isWhitePiece = (p >= WP && p <= WK);
    if ((us == WHITE && !isWhitePiece) || (us == BLACK && isWhitePiece))
      continue;

    uint64_t bb = bitboards[p];
    while (bb) {
      int from = 0;
#if defined(_MSC_VER) && !defined(__clang__)
      unsigned long index;
      _BitScanForward64(&index, bb);
      from = index;
#else
      from = __builtin_ctzll(bb);
#endif
      bb &= bb - 1;

      // Piece Specific Logic
      if (p == WP || p == BP) {
        int dir = (p == WP) ? 8 : -8;
        int to = from + dir;
        int promRank = (p == WP) ? 7 : 0;

        if (to >= 0 && to < 64 && pieceAt(to) == EMPTY) {
          if ((to / 8) == promRank) {
            // Promotion moves (Q, R, B, N)
            Piece promPieces[4] = {(p == WP ? WQ : BQ), (p == WP ? WR : BR),
                                   (p == WP ? WB : BB), (p == WP ? WN : BN)};
            for (Piece prom : promPieces)
              moves.push_back(Move(from, to, prom));
          } else {
            moves.push_back(Move(from, to));
          }

          // Double push (not from promotion rank)
          if ((from / 8) != promRank) {
            int startRank = (p == WP) ? 1 : 6;
            if ((from / 8) == startRank) {
              int toMid = from + dir;
              int to2 = from + 2 * dir;
              if (pieceAt(toMid) == EMPTY && pieceAt(to2) == EMPTY)
                moves.push_back(Move(from, to2));
            }
          }
        }
        // Captures
        for (int c_side : {-1, 1}) {
          int to_c = from + dir + c_side;
          if (to_c >= 0 && to_c < 64 &&
              std::abs((to_c % 8) - (from % 8)) == 1) {
            Piece target = pieceAt(to_c);
            if (target != EMPTY && ((us == WHITE && target >= BP) ||
                                    (us == BLACK && target <= WK))) {
              if ((to_c / 8) == promRank) {
                // Promotion captures
                Piece promPieces[4] = {(p == WP ? WQ : BQ), (p == WP ? WR : BR),
                                       (p == WP ? WB : BB),
                                       (p == WP ? WN : BN)};
                for (Piece prom : promPieces)
                  moves.push_back(Move(from, to_c, prom));
              } else {
                moves.push_back(Move(from, to_c));
              }
            }
          }
        }
      } else if (p == WN || p == BN) {
        for (int d : knightDirs) {
          int to = from + d;
          if (to >= 0 && to < 64) {
            int fileDist = std::abs((to % 8) - (from % 8));
            if (fileDist <= 2) {
              Piece target = pieceAt(to);
              if (target == EMPTY || ((us == WHITE && target >= BP) ||
                                      (us == BLACK && target <= WK)))
                moves.push_back(Move(from, to));
            }
          }
        }
      } else if (p == WK || p == BK) {
        for (int d : queenDirs) {
          int to = from + d;
          if (to >= 0 && to < 64 && std::abs((to % 8) - (from % 8)) <= 1) {
            Piece target = pieceAt(to);
            if (target == EMPTY || ((us == WHITE && target >= BP) ||
                                    (us == BLACK && target <= WK)))
              moves.push_back(Move(from, to));
          }
        }
      } else {
        // Sliders
        const int *dirs = (p == WR || p == BR)
                              ? rookDirs
                              : (p == WB || p == BB ? bishopDirs : queenDirs);
        int numDirs = (p == WQ || p == BQ) ? 8 : 4;
        for (int i = 0; i < numDirs; ++i) {
          int to = from;
          while (true) {
            int nextTo = to + dirs[i];
            if (nextTo < 0 || nextTo >= 64)
              break;
            if (std::abs((nextTo % 8) - (to % 8)) > 2)
              break; // Wrapped board

            Piece target = pieceAt(nextTo);
            if (target == EMPTY) {
              moves.push_back(Move(from, nextTo));
              to = nextTo;
            } else {
              if ((us == WHITE && target >= BP) ||
                  (us == BLACK && target <= WK))
                moves.push_back(Move(from, nextTo));
              break;
            }
          }
        }
      }
    }
  }
  return moves;
}
