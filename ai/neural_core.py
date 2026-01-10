import torch
import torch.nn as nn
import torch.optim as optim
import csv
from pathlib import Path

class IntentNet(nn.Module):
    """Tiny feed-forward net mapping intent context to a scalar score."""
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(5, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Tanh()     # output in [-1,1]
        )

    def forward(self, x):
        return self.layers(x)

def load_intent_data(path="logs/intent_history.csv"):
    X, y = [], []
    path_obj = Path(path)
    if not path_obj.exists():
        print(f"Data file not found: {path}")
        return torch.tensor([]), torch.tensor([])

    with open(path, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or row[0] == "Timestamp": 
                continue # Skip header or empty rows
            if len(row) < 6: 
                continue
                
            try:
                atk, dfs, ctrl, tmp, rsk = map(float, row[1:6])
                # simplistic target: more attack/control → higher score
                # This target logic is a placeholder provided by the design.
                target = 0.2*atk + 0.2*ctrl - 0.2*dfs - 0.2*rsk + 0.1*tmp
                
                X.append([atk, dfs, ctrl, tmp, rsk])
                y.append([target])
            except ValueError:
                continue # Skip malformed rows
                
    if not X:
        return torch.tensor([]), torch.tensor([])
        
    return torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.float32)

def train_intent_net(epochs=100, lr=1e-3):
    X, y = load_intent_data()
    if X.numel() == 0:
        print("No training data available.")
        return None

    model = IntentNet()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.MSELoss()
    
    print(f"Training on {len(X)} samples...")
    for epoch in range(epochs):
        pred = model(X)
        loss = loss_fn(pred, y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        if (epoch+1) % 10 == 0:
            print(f"Epoch {epoch+1}: loss={loss.item():.4f}")
            
    Path("models").mkdir(exist_ok=True)
    torch.save(model.state_dict(), "models/intent_net.pt")
    print("Model saved → models/intent_net.pt")
    return model

def evaluate_context(model, ctx):
    """Return neural evaluation given a flaw_core.IntentContext."""
    # Assuming ctx has attributes: attack, defense, control, tempo, risk
    x = torch.tensor([[ctx.attack, ctx.defense, ctx.control, ctx.tempo, ctx.risk]],
                     dtype=torch.float32)
    with torch.no_grad():
        return model(x).item()

if __name__ == "__main__":
    train_intent_net()
