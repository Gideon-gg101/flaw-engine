import os
import sys

# Add DLL path for Windows
try:
    os.add_dll_directory(r"C:\Users\Administrator\Downloads\winlibs-x86_64-posix-seh-gcc-15.1.0-mingw-w64msvcrt-13.0.0-r4\mingw64\bin")
except AttributeError:
    pass

import torch
import torch.nn as nn
import torch.optim as optim
import random
import flaw_core as fc
from ai.search_controller import FlawEngine
from ai.neural_core import IntentNet

# Helper for side-to-move feature extraction
def features_from_ctx(ctx, side):
    s = 1.0 if side == fc.Color.WHITE else -1.0
    return torch.tensor([
        ctx.attack * s, ctx.defense * s,
        ctx.control * s, ctx.tempo * s, ctx.risk * s
    ], dtype=torch.float32)

def play_self_game(engine, model, depth=2):
    history = []
    # Limit moves to avoid infinite loops in early model stages
    move_count = 0
    while not engine.board.is_game_over() and move_count < 200:
        move, _ = engine.best_move()
        if not move:
            break
        
        # Save snapshot BEFORE move
        # Using Board copy to store state if needed, or just FEN
        fen = engine.board.to_fen()
        # Save ctx and current side
        history.append((fen, fc.IntentContext(engine.ctx.control, engine.ctx.attack, 
                                             engine.ctx.defense, engine.ctx.tempo, 
                                             engine.ctx.risk), engine.board.side_to_move))
        
        engine.board.make_move(move)
        move_count += 1
        
    result = engine.board.get_result()
    # attach result to each pos recorded
    return [(fen, ctx, side, result) for (fen, ctx, side) in history]

def generate_games(n_games=10, depth=2):
    all_data = []
    for i in range(n_games):
        print(f"  Generating game {i+1}/{n_games}...")
        engine = FlawEngine(depth=depth)
        game_data = play_self_game(engine, None, depth) # Using current engine's ctx
        all_data += game_data
    return all_data

def train_on_data(model, data, lr=1e-3, epochs=5):
    if not data:
        print("No data to train on.")
        return
        
    X = torch.stack([features_from_ctx(ctx, side) for fen, ctx, side, result in data])
    y = torch.tensor([[float(result)] for fen, ctx, side, result in data], dtype=torch.float32)
    
    optimizer = optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.MSELoss()
    
    print(f"Training on {len(X)} samples for {epochs} epochs...")
    for e in range(epochs):
        model.train()
        pred = model(X)
        loss = loss_fn(pred, y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        if (e + 1) % 1 == 0:
            print(f"    Epoch {e+1}: loss={loss.item():.4f}")

def reinforcement_train(rounds=3, games_per_round=5):
    print(f"Starting Reinforcement Training: {rounds} rounds, {games_per_round} games each.")
    model = IntentNet()
    # Try loading existing if present
    if os.path.exists("models/intent_net.pt"):
        try:
            model.load_state_dict(torch.load("models/intent_net.pt", map_location="cpu"))
            print("Loaded existing model.")
        except:
            print("Could not load existing model, starting fresh.")
            
    os.makedirs("models", exist_ok=True)
    
    for r in range(rounds):
        print(f"\n--- Round {r+1}/{rounds} ---")
        data = generate_games(n_games=games_per_round, depth=2)
        train_on_data(model, data)
        
        model_path = f"models/intent_net_r{r+1}.pt"
        torch.save(model.state_dict(), model_path)
        # Also save as latest
        torch.save(model.state_dict(), "models/intent_net.pt")
        print(f"Round {r+1} complete. Model saved: {model_path}")

if __name__ == "__main__":
    reinforcement_train(rounds=2, games_per_round=2)
