from flask import Flask, request, send_file, jsonify
import os
import json
import threading

app = Flask(__name__)

# Base directory for the project
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WEIGHTS_PATH = os.path.join(BASE_DIR, "ai", "tuned_weights.json")
RESULTS_PATH = os.path.join(BASE_DIR, "logs", "distributed_results.json")

# Ensure logs directory exists
os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)

# Lock for thread-safe file updates
update_lock = threading.Lock()

@app.route("/get_weights", methods=["GET"])
def get_weights():
    if os.path.exists(WEIGHTS_PATH):
        return send_file(WEIGHTS_PATH)
    return jsonify({"error": "No weights found"}), 404

@app.route("/report_result", methods=["POST"])
def report_result():
    data = request.get_json()
    result = data.get("result") # 1.0 (win), 0.5 (draw), 0.0 (loss)
    
    with update_lock:
        # Update weights based on remote result
        if os.path.exists(WEIGHTS_PATH):
            with open(WEIGHTS_PATH, "r") as f:
                weights = json.load(f)
            
            # Simple learning rule (same as selfplay_trainer but from remote)
            if result > 0.8:
                weights["attack"] *= 1.001
            elif result < 0.2:
                weights["defense"] *= 1.001
            
            with open(WEIGHTS_PATH, "w") as f:
                json.dump(weights, f, indent=2)
                
        # Log to results
        results = []
        if os.path.exists(RESULTS_PATH):
            with open(RESULTS_PATH, "r") as f:
                results = json.load(f)
        
        results.append(data)
        with open(RESULTS_PATH, "w") as f:
            json.dump(results, f, indent=2)

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
