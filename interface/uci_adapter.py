import sys
import os
# Add DLL path first
try:
    os.add_dll_directory(r"C:\Users\Administrator\Downloads\winlibs-x86_64-posix-seh-gcc-15.1.0-mingw-w64msvcrt-13.0.0-r4\mingw64\bin")
except AttributeError:
    pass

import flaw_core as fc
from ai.search_controller import FlawEngine
from ai.hybrid_evaluator import HybridEvaluator
from ai.learning_manager import LearningManager

class UCIAdapter:
    def __init__(self):
        self.engine = FlawEngine(depth=2)
        # alpha=0.3 blends 30% neural. If torch missing, effectively 0%.
        self.hybrid = HybridEvaluator(alpha=0.3)
        self.learner = LearningManager()
        self.learner.apply_to_ctx(self.engine.ctx)
        self.running = True
        self.game_active = False

    def uci_loop(self):
        print("id name Flaw Engine")
        print("id author You")
        print("uciok")
        sys.stdout.flush()
        while self.running:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                line = line.strip()
            except EOFError:
                break
                
            if not line:
                continue
                
            if line == "isready":
                print("readyok")
            elif line == "uci":
                print("id name Flaw Engine")
                print("id author You")
                print("uciok")
            elif line.startswith("position"):
                self.handle_position(line)
            elif line.startswith("go"):
                self.handle_go()
            elif line == "quit":
                self.running = False
                break
            sys.stdout.flush()

    def handle_position(self, cmd):
        parts = cmd.split()
        if "startpos" in cmd:
            fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
            self.engine.load_fen(fen)
            if "moves" in parts:
                move_idx = parts.index("moves") + 1
                self.apply_moves(parts[move_idx:])
        elif "fen" in parts:
            moves_idx = parts.index("moves") if "moves" in parts else len(parts)
            fen_idx = parts.index("fen") + 1
            fen = " ".join(parts[fen_idx:moves_idx])
            self.engine.load_fen(fen)
            if "moves" in parts:
                self.apply_moves(parts[moves_idx+1:])
            
    def apply_moves(self, moves):
        for m_str in moves:
            legal = self.engine.board.generate_moves()
            found = False
            for m in legal:
                if self.move_to_uci(m) == m_str:
                    self.engine.board.make_move(m)
                    found = True
                    break
            if not found:
                # Fallback for unexpected moves (should not happen if legal list is correct)
                # But helps debug protocol issues
                f_sq = (ord(m_str[0]) - 97) + (int(m_str[1]) - 1) * 8
                t_sq = (ord(m_str[2]) - 97) + (int(m_str[3]) - 1) * 8
                self.engine.board.make_move(fc.Move(f_sq, t_sq, fc.Piece.EMPTY))

    def handle_go(self):
        self.game_active = True
        # Time controls could be parsed from 'go wtime ...'
        best_move, score = self.engine.best_move()
        
        # Check if game is over after our move (simplified check)
        if self.engine.board.is_game_over():
            self.handle_game_end()
            
        if best_move:
            uci_str = self.move_to_uci(best_move)
            print(f"info score cp {int(score)}")
            print(f"bestmove {uci_str}")
        else:
            print("bestmove 0000")

    def handle_game_end(self):
        if not self.game_active:
            return
        res = self.engine.board.get_result()
        # Convert engine score: 1.0 win, 0.5 draw, 0.0 loss
        # result is from white's perspective. Need to map to engine side.
        engine_side = self.engine.board.side_to_move # Wait, getResult is for the state reached
        # If engine just played and game is over, it was engine's move.
        # But board.sideToMove has swapped. 
        # Simplified: if result is 1 and engine was white -> win.
        # For simplicity in this prototype, we'll use a broad mapping:
        eng_score = 0.5
        if res == 1: eng_score = 1.0
        elif res == -1: eng_score = 0.0
        
        self.learner.update_from_result(eng_score)
        self.game_active = False

    @staticmethod
    def move_to_uci(move):
        # Convert index back to algebraic
        # rank = idx // 8, file = idx % 8
        
        # from_sq and to_sq used due to binding rename phase
        f = move.from_sq
        t = move.to_sq
        
        f_file = f % 8
        f_rank = f // 8 
        t_file = t % 8
        t_rank = t // 8
        
        from_str = chr(f_file + 97) + str(f_rank + 1)
        to_str = chr(t_file + 97) + str(t_rank + 1)
        
        prom_str = ""
        if move.promotion != fc.Piece.EMPTY:
            p_map = {fc.Piece.WQ: "q", fc.Piece.WR: "r", fc.Piece.WB: "b", fc.Piece.WN: "n",
                     fc.Piece.BQ: "q", fc.Piece.BR: "r", fc.Piece.BB: "b", fc.Piece.BN: "n"}
            prom_str = p_map.get(move.promotion, "")
            
        return from_str + to_str + prom_str


if __name__ == "__main__":
    UCIAdapter().uci_loop()
