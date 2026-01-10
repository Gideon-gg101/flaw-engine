import time
import os
try:
    os.add_dll_directory(r"C:\Users\Administrator\Downloads\winlibs-x86_64-posix-seh-gcc-15.1.0-mingw-w64msvcrt-13.0.0-r4\mingw64\bin")
except AttributeError: pass

from ai.search_controller import FlawEngine

engine = FlawEngine(depth=3)
engine.load_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

print("Starting search (depth 3, 4 threads)...")
start = time.time()
mv, score = engine.best_move()
# Handle case if None (e.g. no moves)
if mv:
    print(f"Best: {mv.from_sq}->{mv.to_sq}, Score: {score}")
else:
    print("No move found.")
print(f"Elapsed: {time.time() - start:.4f} s")
