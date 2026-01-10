import json
import os
import flaw_core as fc

class LearningManager:
    """Manages persistent tuning of intent weights based on game outcomes."""
    def __init__(self, path="ai/tuned_weights.json"):
        self.path = path
        self.weights = self.load()

    def load(self):
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                return json.load(f)
        return {
            "attack": 1.0,
            "defense": 1.0,
            "control": 1.0,
            "tempo": 1.0,
            "risk": 1.0
        }

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(self.weights, f, indent=2)

    def apply_to_ctx(self, ctx):
        ctx.attack = self.weights["attack"]
        ctx.defense = self.weights["defense"]
        ctx.control = self.weights["control"]
        ctx.tempo = self.weights["tempo"]
        ctx.risk = self.weights["risk"]

    def update_from_result(self, result):
        """result: 1.0 (win), 0.5 (draw), 0.0 (loss) from engine perspective."""
        print(f"info string Learning from game result: {result}")
        if result > 0.8: # Win
            self.weights["attack"] *= 1.01
            self.weights["control"] *= 1.01
        elif result < 0.2: # Loss
            self.weights["defense"] *= 1.02
            self.weights["risk"] *= 0.98
        else: # Draw
            self.weights["tempo"] *= 1.005
            
        self.save()
