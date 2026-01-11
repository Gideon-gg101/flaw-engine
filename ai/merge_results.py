import json
import os
import glob
import sys

# Paths (Absolute or Relative to project root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEIGHTS_PATH = os.path.join(BASE_DIR, "ai", "tuned_weights.json")

def merge_results(results_dir):
    """
    Reads all JSON files in the results_dir and updates tuned_weights.json.
    """
    if not os.path.exists(WEIGHTS_PATH):
        print(f"❌ Error: Could not find weights at {WEIGHTS_PATH}")
        return

    # 1. Load current weights
    with open(WEIGHTS_PATH, "r") as f:
        weights = json.load(f)

    # 2. Find all result files
    json_files = glob.glob(os.path.join(results_dir, "results_worker_*.json"))
    if not json_files:
        # Also check for just worker_*.json or results_*.json
        json_files = glob.glob(os.path.join(results_dir, "results_*.json"))
        
    if not json_files:
        print(f"⚠️ No result files found in {results_dir}")
        return

    print(f"🔍 Found {len(json_files)} result files. Processing...")

    total_games = 0
    wins = 0
    losses = 0

    # 3. Process each file
    for json_file in json_files:
        try:
            with open(json_file, "r") as f:
                data = json.load(f)
            
            for entry in data:
                res = entry.get("result", 0.5)
                total_games += 1
                
                # Stable linear learning rule
                if res > 0.8:
                    weights["attack"] += 0.001
                    wins += 1
                elif res < 0.2:
                    weights["defense"] += 0.001
                    losses += 1
        except Exception as e:
            print(f"❌ Error reading {json_file}: {e}")

    # 4. Save updated weights
    with open(WEIGHTS_PATH, "w") as f:
        json.dump(weights, f, indent=2)

    print(f"✅ Success! Processed {total_games} games.")
    print(f"📊 Stats: Wins: {wins}, Losses: {losses}, Draws: {total_games - wins - losses}")
    print(f"⚖️ New Weights: Attack={weights['attack']:.4f}, Defense={weights['defense']:.4f}")

if __name__ == "__main__":
    # If a directory is passed in, use it; otherwise use current directory
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    merge_results(target_dir)
