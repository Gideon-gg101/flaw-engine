import os
try:
    os.add_dll_directory(r"C:\Users\Administrator\Downloads\winlibs-x86_64-posix-seh-gcc-15.1.0-mingw-w64msvcrt-13.0.0-r4\mingw64\bin")
except AttributeError:
    pass

import random
import copy
import flaw_core as fc
from ai.search_controller import FlawEngine

from ai.data_export import DataLogger

from ai.data_export import DataLogger

def run_isolated_game(depth, base_ctx_weights):
    # Isolated function for multiprocessing
    import os
    try:
        os.add_dll_directory(r"C:\Users\Administrator\Downloads\winlibs-x86_64-posix-seh-gcc-15.1.0-mingw-w64msvcrt-13.0.0-r4\mingw64\bin")
    except AttributeError:
        pass
    import flaw_core as fc
    from ai.search_controller import FlawEngine
    
    # Reload weights into a fresh context
    ctx = fc.IntentContext(
        base_ctx_weights['attack'],
        base_ctx_weights['defense'],
        base_ctx_weights['control'],
        base_ctx_weights['tempo'],
        base_ctx_weights['risk']
    )
    
    engine = FlawEngine(depth=depth)
    engine.ctx = ctx
    engine.load_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    
    move_count = 0
    history = []
    while move_count < 150 and not engine.board.is_game_over():
        mv, _ = engine.best_move()
        if not mv: break
        
        # Snapshot (simplified for speed in turbo)
        # fen = engine.board.to_fen()
        
        engine.board.make_move(mv)
        move_count += 1
        
    res = engine.board.get_result()
    return res

class SelfPlayTrainer:
    def __init__(self, depth=2, games=50):
        self.depth = depth
        self.games = games
        self.history = []  # [(fen, move, result)]
        self.base_ctx = fc.IntentContext(1, 1, 1, 1, 1)
        self.logger = DataLogger()

    def play_one_game(self):
        engine = FlawEngine(depth=self.depth)
        # Inject the evolving context
        engine.ctx = self.base_ctx 
        
        engine.load_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        result = 0
        move_count = 0
        
        # Determine checkmate/stalemate simplified
        while move_count < 200:
            move, score = engine.best_move()
            if move is None:
                # No legal moves. 
                # If side to move is White, and no moves, White lost (assuming mate for now) -> Result -1
                # If side to move is Black, and no moves, Black lost -> Result 1
                if engine.board.side_to_move == fc.Color.WHITE:
                    result = -1
                else:
                    result = 1
                break
                
            # Snapshot board state (using copy constructor via python binding)
            fen_snapshot = fc.Board(engine.board)
            
            engine.board.make_move(move)
            move_count += 1
            
            # Record from perspective of side to move?
            # History: (State before move, Move taken, Final Result)
            self.history.append((fen_snapshot, move, result))
            
            # Insufficient material check could be here...
            
        return result

    def train(self):
        print(f"Training started: {self.games} games (Depth: {self.depth})")
        for g in range(self.games):
            print(f"Starting self-play game {g+1}/{self.games}")
            
            # Convert ctx to dict for isolated run
            weights = {
                "attack": self.base_ctx.attack,
                "defense": self.base_ctx.defense,
                "control": self.base_ctx.control,
                "tempo": self.base_ctx.tempo,
                "risk": self.base_ctx.risk
            }
            
            result = run_isolated_game(self.depth, weights)
            
            # Backfill result into history for the moves of this game
            # (Snippet didn't do this, but usually you want the result associated with the moves)
            # But adhering to snippet logic: just update heuristic weights based on game result.
            
            # simple update rule: 
            # If White won (1), boost White's heuristic parameters?
            # Wait, base_ctx is shared by BOTH sides in self-play?
            # If both use same ctx, self-play doesn't distinguish "My ctx" vs "Opponent ctx".
            # This is a "global parameter tuning". 
            # The snippet logic: if result > 0 (White won): boost attack/control.
            # This implies "Winning style was high attack/control".
            # But both sides used the SAME parameters.
            # So if White (First player) won, maybe first move advantage + parameters = win.
            # Validating the snippet's intent: "wins -> increase attack". 
            
            if result > 0:
                self.base_ctx.attack *= 1.05
                self.base_ctx.control *= 1.02
                print("White won. Increasing Attack/Control.")
            elif result < 0:
                self.base_ctx.defense *= 1.05
                self.base_ctx.risk *= 0.95
                print("Black won. Increasing Defense/Reducing Risk.")
            else:
                print("Draw.")
                
            self.logger.log_game(g+1, self.history, self.base_ctx)
            # Clear history for next game
            self.history = []
            
            print(f"Game {g+1} result: {result}")
            print(f"Updated context: atk={self.base_ctx.attack:.2f}, def={self.base_ctx.defense:.2f}, risk={self.base_ctx.risk:.2f}")

if __name__ == "__main__":
    trainer = SelfPlayTrainer(depth=2, games=10)
    trainer.train()
