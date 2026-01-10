import subprocess
import os
import time
import flaw_core as fc
from ai.search_controller import FlawEngine
from ai.selfplay_trainer import SelfPlayTrainer

class UCIEngineWrapper:
    """Wrapper for external UCI engines (like Stockfish)."""
    def __init__(self, path):
        self.path = path
        self.proc = subprocess.Popen(
            [path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        self.send("uci")
        self.read_until("uciok")

    def send(self, cmd):
        self.proc.stdin.write(cmd + "\n")
        self.proc.stdin.flush()

    def read_until(self, target):
        while True:
            line = self.proc.stdout.readline().strip()
            if target in line:
                return line

    def get_bestmove(self, fen, depth=2):
        self.send(f"position fen {fen}")
        self.send(f"go depth {depth}")
        line = self.read_until("bestmove")
        # bestmove e2e4 ...
        parts = line.split()
        return parts[1]

    def quit(self):
        self.send("quit")
        self.proc.terminate()

class ExternalSparring:
    def __init__(self, external_engine_path):
        self.external_path = external_engine_path
        self.flaw = FlawEngine(depth=2)
        self.trainer = SelfPlayTrainer(depth=2) # Use trainer for weight updates

    def play_game(self):
        external = UCIEngineWrapper(self.external_path)
        self.flaw.load_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        
        move_count = 0
        while not self.flaw.board.is_game_over() and move_count < 150:
            side = self.flaw.board.side_to_move
            fen = self.flaw.board.to_fen()
            
            if side == fc.Color.WHITE:
                # Flaw plays White
                mv, _ = self.flaw.best_move()
                if not mv: break
                self.flaw.board.make_move(mv)
            else:
                # External plays Black
                uci_move = external.get_bestmove(fen, depth=2)
                # Parse UCI (e.g., e2e4) to fc.Move
                f = (ord(uci_move[0]) - 97) + (int(uci_move[1]) - 1) * 8
                t = (ord(uci_move[2]) - 97) + (int(uci_move[3]) - 1) * 8
                self.flaw.board.make_move(fc.Move(f, t, fc.Piece.EMPTY))
            
            move_count += 1
            
        result = self.flaw.board.get_result()
        external.quit()
        return result

    def spar(self, n_games=5):
        print(f"Starting sparring session against {os.path.basename(self.external_path)}")
        for i in range(n_games):
            print(f"  Game {i+1}/{n_games}...")
            res = self.play_game()
            
            # Learning feedback
            if res > 0:
                print("    Flaw won! Boosting confidence parameters.")
                self.trainer.base_ctx.attack *= 1.02
            elif res < 0:
                print("    Flaw lost. Analyzing defensive failures.")
                self.trainer.base_ctx.defense *= 1.05
                self.trainer.base_ctx.risk *= 0.95
            else:
                print("    Draw.")
            
            print(f"    New Context: atk={self.trainer.base_ctx.attack:.2f}, def={self.trainer.base_ctx.defense:.2f}")

if __name__ == "__main__":
    # Example setup (requires path to an external engine)
    sf_path = r"C:\Users\Administrator\Desktop\stockfish\stockfish-windows-x86-64-avx2.exe"
    if os.path.exists(sf_path):
        sparring = ExternalSparring(sf_path)
        sparring.spar(n_games=3)
    else:
        print(f"External engine not found at {sf_path}. Please update the path to test.")
