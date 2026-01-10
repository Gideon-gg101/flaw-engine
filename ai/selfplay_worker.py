import requests
import os
import time
import random
import argparse
from ai.selfplay_trainer import run_isolated_game

class DistributedWorker:
    def __init__(self, master_url, depth=1):
        self.master_url = master_url
        self.depth = depth
        self.worker_id = f"worker_{random.randint(1000, 9999)}"

    def fetch_weights(self):
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
    parser.add_argument("--master", type=str, default="http://localhost:8000", help="URL of the local weight server")
    parser.add_argument("--depth", type=int, default=1, help="Search depth for games")
    args = parser.parse_args()

    # Ensure URL is clean
    master_url = args.master.rstrip('/')
    
    worker = DistributedWorker(master_url, depth=args.depth)
    worker.run()
