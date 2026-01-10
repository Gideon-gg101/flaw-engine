import requests
import os
import time
import random
import argparse
from ai.selfplay_trainer import run_isolated_game

class DistributedWorker:
    def __init__(self, master_url, depth=1):
        self.master_url = master_url.rstrip('/') if master_url else None
        self.is_offline = not self.master_url or "OFFLINE" in self.master_url.upper()
        self.depth = depth
        self.worker_id = f"worker_{random.randint(1000, 9999)}"
        self.offline_file = f"results_{self.worker_id}.json"
        self.results_cache = []

    def fetch_weights(self):
        if self.is_offline:
            return {"attack": 1.0, "defense": 1.0, "control": 1.0, "tempo": 1.0, "risk": 1.0}
        try:
            res = requests.get(f"{self.master_url}/get_weights", timeout=10)
            if res.status_code == 200:
                return res.json()
            else:
                print(f"Server returned status {res.status_code}")
        except Exception as e:
            print(f"Failed to fetch weights from {self.master_url}: {e}")
            print("Using defaults.")
        return {"attack": 1.0, "defense": 1.0, "control": 1.0, "tempo": 1.0, "risk": 1.0}

    def run(self):
        print(f"Worker {self.worker_id} starting...")
        while True:
            weights = self.fetch_weights()
            print(f"Playing game with current master weights...")
            
            # Run one game (using existing turbo logic)
            result = run_isolated_game(self.depth, weights)
            
            # Normalize result (from white's perspective)
            # Result is 1, 0, or -1. Map to 1.0, 0.5, 0.0
            norm_res = 0.5
            if result == 1: norm_res = 1.0
            elif result == -1: norm_res = 0.0
            
            print(f"Game finished. Result: {norm_res}. Reporting to master...")
            
            if self.is_offline:
                import json
                self.results_cache.append({
                    "worker_id": self.worker_id,
                    "result": norm_res,
                    "timestamp": time.time()
                })
                with open(self.offline_file, "w") as f:
                    json.dump(self.results_cache, f, indent=2)
                print(f"Result saved locally to {self.offline_file}")
            else:
                try:
                    res = requests.post(f"{self.master_url}/report_result", json={
                        "worker_id": self.worker_id,
                        "result": norm_res,
                        "timestamp": time.time()
                    }, timeout=10)
                    if res.status_code != 200:
                        print(f"Master alert: Server returned {res.status_code}")
                except Exception as e:
                    print(f"Failed to report result to {self.master_url}: {e}")
            
            time.sleep(1) # Small gap

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flaw Distributed Worker")
    parser.add_argument("--master", type=str, default=None, help="URL of the local weight server (or leave empty for offline mode)")
    parser.add_argument("--depth", type=int, default=1, help="Search depth for games")
    args = parser.parse_args()

    worker = DistributedWorker(args.master, depth=args.depth)
    if worker.is_offline:
        print("🚀 RUNNING IN OFFLINE MODE - Results will be saved to disk.")
    else:
        print(f"🚀 RUNNING IN LIVE MODE - Connected to {worker.master_url}")
    worker.run()
