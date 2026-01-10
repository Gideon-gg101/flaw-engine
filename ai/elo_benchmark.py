import os
import math
import random
try:
    import torch
    from ai.neural_core import IntentNet
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    print("Warning: torch not found. Benchmarking will use symbolic search only.")

from ai.search_controller import FlawEngine


# Windows DLL path
try:
    os.add_dll_directory(r"C:\Users\Administrator\Downloads\winlibs-x86_64-posix-seh-gcc-15.1.0-mingw-w64msvcrt-13.0.0-r4\mingw64\bin")
except AttributeError:
    pass

class EloSystem:
    def __init__(self, k=16):
        self.k = k
        self.ratings = {}

    def expected(self, ra, rb):
        return 1 / (1 + 10 ** ((rb - ra) / 400))

    def update(self, name_a, name_b, score_a):
        ra = self.ratings.get(name_a, 1500)
        rb = self.ratings.get(name_b, 1500)
        ea = self.expected(ra, rb)
        eb = self.expected(rb, ra)
        
        # score_a: percentage of points won by A (1 for win, 0.5 for draw, 0 for loss)
        self.ratings[name_a] = ra + self.k * (score_a - ea)
        self.ratings[name_b] = rb + self.k * ((1 - score_a) - eb)

def play_match(model_path_a, model_path_b, depth=2):
    """Plays a single game between two models. Alternating sides is recommended outside this call."""
    engine = FlawEngine(depth=depth)
    
    # In a real scenario, we'd need to actually swap models in engine.ctx or hybrid eval.
    # For now, this is a placeholder loop demonstrating communication.
    
    move_count = 0
    while not engine.board.is_game_over() and move_count < 100:
        mv, _ = engine.best_move()
        if not mv:
            break
        engine.board.make_move(mv)
        move_count += 1
        
    res = engine.board.get_result()
    if res > 0: return 1.0, 0.0      # White wins
    elif res < 0: return 0.0, 1.0    # Black wins
    else: return 0.5, 0.5           # Draw

def evaluate_versions(model_paths, n_games=4):
    elo = EloSystem()
    
    # Initialize all with 1500
    for p in model_paths:
        elo.ratings[os.path.basename(p)] = 1500

    for i in range(len(model_paths)):
        for j in range(i + 1, len(model_paths)):
            pa, pb = model_paths[i], model_paths[j]
            name_a, name_b = os.path.basename(pa), os.path.basename(pb)
            
            print(f"Match: {name_a} vs {name_b}")
            
            points_a = 0
            for g in range(n_games):
                # Note: To be fair, one should alternate colors.
                # Here we assume model_a is simply the current active engine behavior.
                # In full implementation, FlawEngine would take a model path.
                res_a, res_b = play_match(pa, pb)
                points_a += res_a
                print(f"  Game {g+1}: {res_a}-{res_b}")
                
            elo.update(name_a, name_b, points_a / n_games)
            
    return elo.ratings

if __name__ == "__main__":
    # Example usage:
    # check for existing models in models/
    model_dir = "models"
    if os.path.exists(model_dir):
        checkpoints = [os.path.join(model_dir, f) for f in os.listdir(model_dir) if f.endswith(".pt")]
        if len(checkpoints) >= 2:
            results = evaluate_versions(checkpoints[:3]) # test first 3 found
            print("\nFinal Elo Ratings:")
            for name, rating in sorted(results.items(), key=lambda x: x[1], reverse=True):
                print(f"  {name}: {rating:.1f}")
        else:
            print("Not enough checkpoints to run benchmark.")
    else:
        print("No models directory found.")
