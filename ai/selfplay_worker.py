import requests
import os
import time
import random
from ai.selfplay_trainer import run_isolated_game

class DistributedWorker:
    def __init__(self, master_url, depth=1):
        self.master_url = master_url
        self.depth = depth
        self.worker_id = f"worker_{random.randint(1000, 9999)}"

    def fetch_weights(self):
        try:
            res = requests.get(f"{self.master_url}/get_weights")
            if res.status_code == 200:
                return res.json()
        except:
            print("Failed to fetch weights, using defaults.")
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
                requests.post(f"{self.master_url}/report_result", json={
                    "worker_id": self.worker_id,
                    "result": norm_res,
                    "timestamp": time.time()
                })
            except:
                print("Failed to report result.")
            
            time.sleep(1) # Small gap

if __name__ == "__main__":
    # In Colab/Cloud, you would replace this with the public URL of your local master
    MASTER_URL = "http://localhost:8000"
    worker = DistributedWorker(MASTER_URL, depth=1)
    worker.run()
