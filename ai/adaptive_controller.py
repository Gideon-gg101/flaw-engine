import math
import json
import os
import flaw_core as fc
from ai.search_controller import FlawEngine
from ai.hybrid_evaluator import HybridEvaluator

class PlayerProfile:
    def __init__(self, name="player", rating=1200, k=32):
        self.name = name
        self.rating = rating
        self.k = k

    def expected_score(self, opponent_rating):
        return 1 / (1 + 10 ** ((opponent_rating - self.rating) / 400))

    def update_rating(self, opponent_rating, score):
        expected = self.expected_score(opponent_rating)
        self.rating += self.k * (score - expected)
        # Keep rating in a reasonable range
        self.rating = max(400, min(3000, self.rating))

    def save(self, path="player_profile.json"):
        with open(path, "w") as f:
            json.dump({"name": self.name, "rating": self.rating}, f)

    @classmethod
    def load(cls, path="player_profile.json"):
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                return cls(name=data.get("name", "player"), rating=data.get("rating", 1200))
        return cls()

class AdaptiveFlaw:
    def __init__(self, player_profile):
        self.profile = player_profile
        self.engine = FlawEngine(depth=2)
        self.hybrid = HybridEvaluator(alpha=0.5)
        self.target_rating = 1500  # Baseline for depth 2

    def adapt_parameters(self):
        diff = self.profile.rating - self.target_rating
        
        # Adjust depth: stronger players -> deeper search
        # Rating 1500 -> depth 2
        # Rating 1900 -> depth 4
        # Rating 2300 -> depth 6
        new_depth = 2 + max(0, int(diff // 200))
        self.engine.depth = min(8, new_depth) # Cap at 8 for safety
        
        # Adjust neural blend: 
        # Low Elo: More "intuitive" (higher alpha favoring neural/symbolic mix)
        # High Elo: More "tactical" (lower alpha favoring raw C++ search depth/accuracy)
        # Note: In our current HybridEvaluator, alpha blends C++ and Neural.
        # If alpha is 0.8, it's 80% neural. If 0.1, it's 10% neural.
        new_alpha = 0.5 - (diff / 2000)
        self.hybrid.alpha = max(0.1, min(0.8, new_alpha))
        
        # Adjust risk preference in IntentContext
        # High Elo players handle risk better/punish it more, so engine plays safer?
        # Or more aggressive? Let's say higher risk for higher Elo challenges.
        self.engine.ctx.risk = 0.5 + (diff / 4000)
        
        return self.engine.depth, self.hybrid.alpha

    def best_move(self):
        depth, alpha = self.adapt_parameters()
        return self.engine.best_move()

    def load_fen(self, fen):
        self.engine.load_fen(fen)
