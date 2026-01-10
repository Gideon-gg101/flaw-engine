import json
import itertools
import random
import os
from ai.adaptive_controller import PlayerProfile
from ai.elo_benchmark import EloSystem

class TournamentManager:
    def __init__(self, player_names):
        self.players = {n: PlayerProfile.load(f"players/{n}.json") if os.path.exists(f"players/{n}.json") else PlayerProfile(n) for n in player_names}
        self.elo = EloSystem()
        for n in player_names:
            self.elo.ratings[n] = self.players[n].rating
        
        os.makedirs("players", exist_ok=True)
        os.makedirs("results", exist_ok=True)

    def pairings(self):
        # Round robin pairs
        return list(itertools.combinations(self.players.keys(), 2))

    def play_match(self, p1, p2):
        # In a real scenario, this would call engine matches.
        # For the prototype, we simulate results based on current rating diffs
        r1 = self.elo.ratings[p1]
        r2 = self.elo.ratings[p2]
        
        expected = 1 / (1 + 10 ** ((r2 - r1) / 400))
        
        # Roll for outcome
        roll = random.random()
        if roll < expected:
            outcome = 1.0  # p1 wins
        elif roll < expected + 0.1: # 10% draw chance
            outcome = 0.5  # draw
        else:
            outcome = 0.0  # p2 wins
            
        self.elo.update(p1, p2, outcome)
        return outcome

    def run(self):
        results = []
        for p1, p2 in self.pairings():
            res = self.play_match(p1, p2)
            results.append({"white": p1, "black": p2, "score": res})
            
        # Update player profiles with new ratings
        for n, profile in self.players.items():
            profile.rating = self.elo.ratings[n]
            profile.save(f"players/{n}.json")
            
        self.save_summary(results)
        return self.elo.ratings

    def save_summary(self, results):
        with open("results/tournament_latest.json", "w") as f:
            json.dump(results, f, indent=2)
        with open("leaderboard.json", "w") as f:
            json.dump(self.elo.ratings, f, indent=2)
