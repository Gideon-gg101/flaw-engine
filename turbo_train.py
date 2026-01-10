import os
import sys

# Add DLL path for MinGW dependencies
try:
    os.add_dll_directory(r"C:\Users\Administrator\Downloads\winlibs-x86_64-posix-seh-gcc-15.1.0-mingw-w64msvcrt-13.0.0-r4\mingw64\bin")
except AttributeError:
    pass

import multiprocessing
from concurrent.futures import ProcessPoolExecutor
import flaw_core as fc
from ai.selfplay_trainer import run_isolated_game
from ai.learning_manager import LearningManager

def turbo_train(total_games=100, batch_size=10, depth=1):
    print(f"🚀 TURBO TRAINING STARTING")
    print(f"Target: {total_games} games | Batch Size: {batch_size} | Depth: {depth}")
    
    learner = LearningManager()
    cores = multiprocessing.cpu_count()
    print(f"Detected {cores} CPU cores. Unleashing parallel power...")
    
    completed = 0
    while completed < total_games:
        current_batch = min(batch_size, total_games - completed)
        print(f"\n--- Batch: {completed // batch_size + 1} ({current_batch} games) ---")
        
        # Prepare current weights
        weights = learner.weights
        
        # Run batch in parallel
        results = []
        with ProcessPoolExecutor(max_workers=cores) as executor:
            futures = [executor.submit(run_isolated_game, depth, weights) for _ in range(current_batch)]
            for future in futures:
                results.append(future.result())
        
        # Aggregate results
        wins = results.count(1)
        losses = results.count(-1)
        draws = results.count(0)
        
        print(f"Batch Results: White Wins: {wins}, Black Wins: {losses}, Draws: {draws}")
        
        # Update weights based on aggregate (Average score)
        # Score from White's perspective
        avg_score = (wins * 1.0 + draws * 0.5) / current_batch
        learner.update_from_result(avg_score)
        
        completed += current_batch
        print(f"Progress: {completed}/{total_games} games complete.")
        print(f"Current Weights: Atk={learner.weights['attack']:.2f}, Def={learner.weights['defense']:.2f}")

if __name__ == "__main__":
    # Ensure multiprocessing works on Windows
    multiprocessing.freeze_support()
    
    games = 20
    if len(sys.argv) > 1:
        games = int(sys.argv[1])
        
    turbo_train(total_games=games, batch_size=10, depth=1)
