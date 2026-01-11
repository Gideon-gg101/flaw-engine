import os
import random
import numpy as np
import chess
import json
from .mcts import MCTSGame, mcts_search
from .neural_core import TinyAlphaZero

def run_self_play(net, num_games=100, sims_per_move=10):
    replay_buffer = []

    for game_idx in range(num_games):
        game = MCTSGame()
        history = [] # (state, policy_target)
        
        print(f"Starting game {game_idx+1}/{num_games}...", end="", flush=True)
        
        while not game.is_game_over() and len(game.board.move_stack) < 200:
            root = mcts_search(game, net, sims=sims_per_move)
            if not root: break
            
            # Policy target from visit counts
            policy_target = np.zeros(4096)
            total_visits = sum(child.visit_count for child in root.children.values())
            
            if total_visits > 0:
                for move, child in root.children.items():
                    idx = move.from_square * 64 + move.to_square
                    policy_target[idx] = child.visit_count / total_visits
            
            history.append((game.to_tensor().flatten(), policy_target))
            
            # Selection (Exploration/Exploitation)
            if len(game.board.move_stack) < 30:
                moves = list(root.children.keys())
                probs = [child.visit_count / total_visits for child in root.children.values()]
                move = random.choices(moves, weights=probs)[0]
            else:
                move = max(root.children.items(), key=lambda x: x[1].visit_count)[0]
                
            game.make_move(move)
            print(".", end="", flush=True)

        result = game.result()
        print(f" Done. Result: {result}")
        
        # Add to buffer with outcome (flipping sign for side-to-move)
        # In history, white moved at index 0, 2, 4...
        # Result is from white's perspective.
        for i, (state, pi) in enumerate(history):
            turn_result = result if i % 2 == 0 else -result
            replay_buffer.append((state, pi, turn_result))

        # Train on recent buffer
        if len(replay_buffer) >= 64:
            batch = random.sample(replay_buffer, 64)
            states = np.array([x[0] for x in batch])
            pi_targets = np.array([x[1] for x in batch])
            v_targets = np.array([x[2] for x in batch]).reshape(-1, 1)
            
            loss = net.train_step(states, pi_targets, v_targets)
            print(f" [Train] Loss: {loss:.4f}")
            
            if len(replay_buffer) > 2000:
                replay_buffer = replay_buffer[-2000:]

        if (game_idx + 1) % 5 == 0:
            weights = {
                "W1": net.W1.tolist(), "b1": net.b1.tolist(),
                "Wp": net.Wp.tolist(), "bp": net.bp.tolist(),
                "Wv": net.Wv.tolist(), "bv": net.bv.tolist()
            }
            with open("ai/mcts_weights.json", "w") as f:
                json.dump(weights, f)
            print(f" [Checkpoint] Weights saved at game {game_idx+1}")

    return net

if __name__ == "__main__":
    net = TinyAlphaZero(input_size=13*8*8, hidden_size=256)
    print("🚀 Initializing AlphaZero (CPU) with python-chess...")
    run_self_play(net, num_games=100, sims_per_move=10)
    
    # Final weight save
    weights = {
        "W1": net.W1.tolist(), "b1": net.b1.tolist(),
        "Wp": net.Wp.tolist(), "bp": net.bp.tolist(),
        "Wv": net.Wv.tolist(), "bv": net.bv.tolist()
    }
    with open("ai/mcts_weights.json", "w") as f:
        json.dump(weights, f)
    print("\n✅ Training Complete. Weights: ai/mcts_weights.json")
