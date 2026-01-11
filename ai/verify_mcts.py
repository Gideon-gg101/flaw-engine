import numpy as np
import chess
from ai.mcts import MCTSGame, mcts_search
from ai.neural_core import TinyAlphaZero

def verify():
    net = TinyAlphaZero(input_size=13*8*8, hidden_size=256)
    try:
        net.load("ai/mcts_weights.json")
        print("Loaded existing weights.")
    except:
        print("No weights found, using random.")

    test_fens = [
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", # Start
        "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3", # Ruy Lopez/Italian
    ]

    for fen in test_fens:
        print(f"\nAnalyzing FEN: {fen}")
        board = chess.Board(fen)
        game = MCTSGame(board)
        root = mcts_search(game, net, sims=100)
        
        # Sort moves by visit count
        moves = sorted(root.children.items(), key=lambda x: x[1].visit_count, reverse=True)
        print("Top moves by MCTS visit count:")
        for m, node in moves[:5]:
            print(f"  {m}: {node.visit_count} visits, value: {node.value:.4f}")

if __name__ == "__main__":
    verify()
