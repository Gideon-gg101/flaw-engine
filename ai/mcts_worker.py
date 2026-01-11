import requests
import os
import time
import random
import argparse
import numpy as np
import chess
from .mcts import MCTSGame, mcts_search
from .neural_core import TinyAlphaZero

class MCTSWorker:
    def __init__(self, master_url, sims=25):
        self.master_url = master_url.rstrip('/') if master_url else None
        self.sims = sims
        self.net = TinyAlphaZero(input_size=13*8*8, hidden_size=256)
        self.worker_id = f"mcts_worker_{random.randint(1000, 9999)}"

    def fetch_weights(self):
        if not self.master_url:
            return False
        try:
            res = requests.get(f"{self.master_url}/get_mcts_weights", timeout=10)
            if res.status_code == 200:
                with open("temp_weights.json", "w") as f:
                    f.write(res.text)
                self.net.load("temp_weights.json")
                return True
        except Exception as e:
            print(f"Failed to fetch MCTS weights: {e}")
        return False

    def run_game(self):
        game = MCTSGame()
        history = []
        
        while not game.is_game_over() and len(game.board.move_stack) < 200:
            root = mcts_search(game, self.net, sims=self.sims)
            if not root: break
            
            # Policy target
            policy_target = np.zeros(4096)
            total_visits = sum(child.visit_count for child in root.children.values())
            if total_visits > 0:
                for move, child in root.children.items():
                    idx = move.from_square * 64 + move.to_square
                    policy_target[idx] = child.visit_count / total_visits
            
            history.append((game.to_tensor().flatten().tolist(), policy_target.tolist()))
            
            # Proportional move selection for exploration
            moves = list(root.children.keys())
            probs = [child.visit_count / total_visits for child in root.children.values()]
            move = random.choices(moves, weights=probs)[0]
            game.make_move(move)

        result = game.result()
        # Prepare triplets
        triplets = []
        for i, (state, pi) in enumerate(history):
            turn_result = result if i % 2 == 0 else -result
            triplets.append((state, pi, turn_result))
        
        return triplets

    def report_data(self, triplets):
        if not self.master_url:
            return
        try:
            requests.post(f"{self.master_url}/report_mcts_data", json=triplets, timeout=30)
            print(f"Reported {len(triplets)} triplets.")
        except Exception as e:
            print(f"Failed to report data: {e}")

    def run(self, duration_mins=10):
        start_time = time.time()
        print(f"Worker {self.worker_id} starting for {duration_mins} minutes...")
        
        while (time.time() - start_time) < (duration_mins * 60):
            self.fetch_weights()
            triplets = self.run_game()
            self.report_data(triplets)
            print(f"Time left: {int((duration_mins * 60 - (time.time() - start_time)) / 60)} mins")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--master", type=str, required=True)
    parser.add_argument("--sims", type=int, default=25)
    parser.add_argument("--duration", type=int, default=10)
    args = parser.parse_args()

    worker = MCTSWorker(args.master, sims=args.sims)
    worker.run(duration_mins=args.duration)
