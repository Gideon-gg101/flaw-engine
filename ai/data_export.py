import csv
from datetime import datetime
from pathlib import Path

class DataLogger:
    def __init__(self, path="logs"):
        self.path = Path(path)
        self.path.mkdir(exist_ok=True, parents=True)

    def log_game(self, game_id, history, context):
        """Save moves and intent context after a self-play game."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file = self.path / f"game_{game_id}_{timestamp}.csv"
        with open(file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Move#", "From", "To", "Result"])
            for idx, (fen, move, result) in enumerate(history):
                # Using from_sq/to_sq to match C++ bindings
                writer.writerow([idx, move.from_sq, move.to_sq, result])
        
        # append summary of context
        intent_file = self.path / "intent_history.csv"
        file_exists = intent_file.exists()
        with open(intent_file, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                # Add header for clarity if file is new
                writer.writerow(["Timestamp", "Attack", "Defense", "Control", "Tempo", "Risk"])
                
            writer.writerow([
                datetime.now().isoformat(),
                context.attack, context.defense, context.control,
                context.tempo, context.risk
            ])
