"""
Train the MCTS network using collected cloud data.
"""
import json
import numpy as np
from ai.neural_core import TinyAlphaZero

def train_from_cloud_data(data_file="logs/mcts_data.json", epochs=10, batch_size=64):
    print(f"📊 Loading cloud training data from {data_file}...")
    
    with open(data_file, "r") as f:
        triplets = json.load(f)
    
    print(f"✅ Loaded {len(triplets)} training examples\n")
    
    # Load existing weights
    net = TinyAlphaZero(input_size=13*8*8, hidden_size=256)
    net.load("ai/mcts_weights.json")
    print("✅ Loaded existing weights\n")
    
    # Convert to numpy arrays
    states = np.array([t[0] for t in triplets])
    policies = np.array([t[1] for t in triplets])
    values = np.array([t[2] for t in triplets]).reshape(-1, 1)
    
    print(f"🎯 Training for {epochs} epochs...\n")
    
    for epoch in range(epochs):
        # Shuffle data
        indices = np.random.permutation(len(triplets))
        
        epoch_loss = 0
        num_batches = 0
        
        for i in range(0, len(triplets), batch_size):
            batch_indices = indices[i:i+batch_size]
            batch_states = states[batch_indices]
            batch_policies = policies[batch_indices]
            batch_values = values[batch_indices]
            
            loss = net.train_step(batch_states, batch_policies, batch_values, lr=1e-3)
            epoch_loss += loss
            num_batches += 1
        
        avg_loss = epoch_loss / num_batches
        print(f"Epoch {epoch+1}/{epochs}: Loss = {avg_loss:.4f}")
    
    # Save updated weights
    net.save("ai/mcts_weights.json")
    print(f"\n✅ Updated weights saved to ai/mcts_weights.json")
    print(f"📊 Total training examples processed: {len(triplets)}")

if __name__ == "__main__":
    train_from_cloud_data(epochs=10, batch_size=64)
