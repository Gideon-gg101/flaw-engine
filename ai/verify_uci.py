import os
import sys
# Add DLL path
os.add_dll_directory(r"C:\Users\Administrator\Downloads\winlibs-x86_64-posix-seh-gcc-15.1.0-mingw-w64msvcrt-13.0.0-r4\mingw64\bin")
sys.path.append(os.getcwd())

import flaw_core as fc
from interface.uci_adapter import UCIAdapter

def test_uci_special_moves():
    adapter = UCIAdapter()
    
    # 1. Test Castling
    print("Testing Castling (e1g1)...")
    adapter.handle_position("position startpos moves e2e4 e7e5 g1f3 b8c6 f1b5 a7a6 b5a4 g8f6 e1g1")
    fen = adapter.engine.board.to_fen()
    print(f"FEN after castling: {fen}")
    if "r1bqkb1r/1ppp1ppp/p1n2n2/4p3/B3P3/5N2/PPPP1PPP/RNBQ1RK1 b kq - 1 1" in fen:
         print("✅ Castling verified.")
    else:
         print("❌ Castling FAILED.")

    # 2. Test Promotion
    print("\nTesting Promotion (a7a8q)...")
    # Position where white pawn is at a7
    adapter.handle_position("position fen 8/P7/8/8/8/8/8/k6K w - - 0 1 moves a7a8q")
    fen = adapter.engine.board.to_fen()
    print(f"FEN after promotion: {fen}")
    if "Q7/8/8/8/8/8/8/k6K b - - 0 1" in fen:
         print("✅ Promotion verified.")
    else:
         print("❌ Promotion FAILED.")

if __name__ == "__main__":
    test_uci_special_moves()
