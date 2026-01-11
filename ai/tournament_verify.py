"""
Run a tournament between trained and untrained MCTS agents.
"""
import chess
from ai.mcts import MCTSGame, mcts_search
from ai.neural_core import TinyAlphaZero

def play_game(white_net, black_net, max_moves=100, sims=25):
    """Play one game between two networks."""
    game = MCTSGame()
    
    while not game.is_game_over() and len(game.board.move_stack) < max_moves:
        current_net = white_net if game.board.turn == chess.WHITE else black_net
        root = mcts_search(game, current_net, sims=sims)
        
        if not root or not root.children:
            break
        
        # Pick best move by visit count
        move = max(root.children.items(), key=lambda x: x[1].visit_count)[0]
        game.make_move(move)
    
    return game.result()

def run_tournament(num_games=10, sims=25):
    """Run a tournament to measure improvement."""
    print(f"🏆 Running {num_games}-game tournament (Trained vs Untrained)")
    print(f"   Simulations per move: {sims}\n")
    
    trained = TinyAlphaZero(input_size=13*8*8, hidden_size=256)
    trained.load("ai/mcts_weights.json")
    print("✅ Loaded trained weights\n")
    
    untrained = TinyAlphaZero(input_size=13*8*8, hidden_size=256)
    
    results = {"trained_wins": 0, "untrained_wins": 0, "draws": 0}
    
    for i in range(num_games):
        # Alternate colors
        if i % 2 == 0:
            white, black = trained, untrained
            colors = ("Trained", "Untrained")
        else:
            white, black = untrained, trained
            colors = ("Untrained", "Trained")
        
        print(f"Game {i+1}/{num_games}: {colors[0]} (White) vs {colors[1]} (Black)...", end=" ", flush=True)
        result = play_game(white, black, sims=sims)
        
        # Track results from trained's perspective
        if result == 1.0:  # White won
            winner = "Trained" if i % 2 == 0 else "Untrained"
        elif result == -1.0:  # Black won
            winner = "Untrained" if i % 2 == 0 else "Trained"
        else:
            winner = "Draw"
        
        if winner == "Trained":
            results["trained_wins"] += 1
        elif winner == "Untrained":
            results["untrained_wins"] += 1
        else:
            results["draws"] += 1
        
        print(f"Result: {winner}")
    
    print("\n" + "="*60)
    print("📊 FINAL RESULTS")
    print("="*60)
    print(f"Trained Wins:   {results['trained_wins']}/{num_games} ({results['trained_wins']/num_games*100:.1f}%)")
    print(f"Untrained Wins: {results['untrained_wins']}/{num_games} ({results['untrained_wins']/num_games*100:.1f}%)")
    print(f"Draws:          {results['draws']}/{num_games} ({results['draws']/num_games*100:.1f}%)")
    
    score = results['trained_wins'] + 0.5 * results['draws']
    print(f"\nTrained Score: {score}/{num_games} ({score/num_games*100:.1f}%)")
    
    if score > num_games * 0.55:
        print("\n✅ Training is WORKING! Trained agent is stronger.")
    elif score < num_games * 0.45:
        print("\n❌ Something's wrong - untrained is better!")
    else:
        print("\n⚠️  Results inconclusive - might need more games or more training.")

if __name__ == "__main__":
    run_tournament(num_games=10, sims=25)
