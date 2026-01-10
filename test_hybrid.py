import os

# Add DLL path first
try:
    os.add_dll_directory(r"C:\Users\Administrator\Downloads\winlibs-x86_64-posix-seh-gcc-15.1.0-mingw-w64msvcrt-13.0.0-r4\mingw64\bin")
except AttributeError:
    pass

from ai.hybrid_evaluator import HybridEvaluator
import flaw_core as fc

def test_hybrid():
    print("Initializing engine...")
    engine_board = fc.Board()
    engine_board.load_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    ctx = fc.IntentContext(1,1,1,1,1)
    
    print("Initializing HybridEvaluator...")
    hybrid = HybridEvaluator(alpha=0.3)
    
    score = hybrid.evaluate(engine_board, ctx)
    print(f"Evaluated score: {score}")
    
    if hybrid.neural_active:
        print("Neural component: ACTIVE")
    else:
        print("Neural component: INACTIVE (C++ only fallback)")

if __name__ == "__main__":
    test_hybrid()
