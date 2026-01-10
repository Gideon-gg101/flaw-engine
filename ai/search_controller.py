import os
try:
    os.add_dll_directory(r"C:\Users\Administrator\Downloads\winlibs-x86_64-posix-seh-gcc-15.1.0-mingw-w64msvcrt-13.0.0-r4\mingw64\bin")
except AttributeError:
    pass # Python < 3.8

import flaw_core as fc
from concurrent.futures import ThreadPoolExecutor

class FlawEngine:
    def __init__(self, depth=3):
        self.board = fc.Board()
        self.ctx = fc.IntentContext(1,1,1,1,1)
        self.depth = depth

    def load_fen(self, fen: str):
        self.board.load_fen(fen)

    def best_move(self):
        moves = self.board.generate_moves()
        if not moves:
            return None, 0

        def score_move(m):
            try:
                bcopy = fc.Board(self.board)
                bcopy.make_move(m)
                # Call search with larger bounds for deep mates
                val = -fc.search(bcopy, self.depth, -2000000, 2000000, self.ctx)
                return (m, val)
            except Exception:
                return (m, -9999999)

        with ThreadPoolExecutor(max_workers=4) as ex:
            results = list(ex.map(score_move, moves))
            
        if not results:
            return None, 0
            
        return max(results, key=lambda x: x[1])
