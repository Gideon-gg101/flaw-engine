from ai.mcts import MCTSGame, mcts_search
from ai.neural_core import AlphaZeroNet
import time
import torch # Error if torch used? No we switched to numpy
import numpy as np

def benchmark():
    print("Benchmarking...")
    g = MCTSGame()
    s = time.time()
    for _ in range(100):
        t = g.to_tensor()
    print(f"100 tensor conversions: {time.time() - s:.4f}s")
    
    net = AlphaZeroNet()
    s = time.time()
    inp = np.zeros((1, 13, 8, 8), dtype=np.float32)
    for _ in range(100):
        net.forward(inp)
    print(f"100 inferences: {time.time() - s:.4f}s")

if __name__ == "__main__":
    benchmark()
