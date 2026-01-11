"""
Compare untrained vs trained MCTS policy on test positions.
"""
import numpy as np
import chess
from ai.mcts import MCTSGame, mcts_search
from ai.neural_core import TinyAlphaZero

def test_position(fen, description):
    print(f"\n{'='*60}")
    print(f"Position: {description}")
    print(f"FEN: {fen}")
    print(f"{'='*60}")
    
    game = MCTSGame(chess.Board(fen))
    
    # Untrained network
    untrained = TinyAlphaZero(input_size=13*8*8, hidden_size=256)
    print("\n🆕 UNTRAINED Network:")
    root_untrained = mcts_search(game.clone(), untrained, sims=50)
    if root_untrained:
        moves_untrained = sorted(root_untrained.children.items(), 
                                 key=lambda x: x[1].visit_count, reverse=True)[:5]
        for move, node in moves_untrained:
            print(f"  {move.uci()}: {node.visit_count} visits, value: {node.value:.3f}")
    
    # Trained network
    trained = TinyAlphaZero(input_size=13*8*8, hidden_size=256)
    trained.load("ai/mcts_weights.json")
    print("\n🎓 TRAINED Network:")
    root_trained = mcts_search(game.clone(), trained, sims=50)
    if root_trained:
        moves_trained = sorted(root_trained.children.items(), 
                               key=lambda x: x[1].visit_count, reverse=True)[:5]
        for move, node in moves_trained:
            print(f"  {move.uci()}: {node.visit_count} visits, value: {node.value:.3f}")

if __name__ == "__main__":
    print("🔬 Comparing UNTRAINED vs TRAINED MCTS Policy\n")
    
    # Test 1: Starting position
    test_position(
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "Starting Position"
    )
    
    # Test 2: Open position
    test_position(
        "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
        "Open Game (after 1.e4 e5 2.Nf3 Nc6)"
    )
    
    # Test 3: Tactical position (free piece)
    test_position(
        "rnbqkb1r/pppp1ppp/5n2/4p3/4P3/5N2/PPPPQPPP/RNB1KB1R b KQkq - 0 3",
        "Queen hanging on e2 (should capture)"
    )
    
    print("\n\n✅ Comparison complete!")
    print("\n💡 If trained is better, you should see:")
    print("   - More central/development moves in opening")
    print("   - Higher visit counts on objectively strong moves")
    print("   - Ability to spot free pieces in tactical positions")
