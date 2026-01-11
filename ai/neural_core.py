import numpy as np
import os
import json

class TinyAlphaZero:
    """
    A NumPy-only Neural Network for CPU inference.
    Architecture:
      Input: 13x8x8 (flattened to 832)
      Hidden: 64 units (ReLU)
      Policy Head: 4096 units (Linear)
      Value Head: 1 unit (Tanh)
    """
    def __init__(self, input_size=832, hidden_size=64):
        self.input_size = input_size
        self.hidden_size = hidden_size
        
        # Init weights
        # Xavier init
        self.W1 = np.random.randn(input_size, hidden_size) * np.sqrt(2/input_size)
        self.b1 = np.zeros(hidden_size)
        
        self.Wp = np.random.randn(hidden_size, 4096) * np.sqrt(2/hidden_size)
        self.bp = np.zeros(4096)
        
        self.Wv = np.random.randn(hidden_size, 1) * np.sqrt(2/hidden_size)
        self.bv = np.zeros(1)
        
    def forward(self, x):
        # x can be [InputSize] or [Batch, InputSize]
        if x.ndim == 1:
            x_flat = x.reshape(1, -1)
        else:
            x_flat = x.reshape(x.shape[0], -1)
        
        # Layer 1
        h1 = np.maximum(0, np.dot(x_flat, self.W1) + self.b1)
        
        # Policy (Logits)
        policy = np.dot(h1, self.Wp) + self.bp
        
        # Value (Tanh)
        val = np.tanh(np.dot(h1, self.Wv) + self.bv)
        
        return policy, val

    def save(self, path):
         # simple dict save
         data = {
             "W1": self.W1.tolist(), "b1": self.b1.tolist(),
             "Wp": self.Wp.tolist(), "bp": self.bp.tolist(),
             "Wv": self.Wv.tolist(), "bv": self.bv.tolist()
         }
         with open(path, "w") as f:
             json.dump(data, f)
             
    def load(self, path):
        if not os.path.exists(path): return
        with open(path, "r") as f:
            data = json.load(f)
        self.W1 = np.array(data["W1"])
        self.b1 = np.array(data["b1"])
        self.Wp = np.array(data["Wp"])
        self.bp = np.array(data["bp"])
        self.Wv = np.array(data["Wv"])
        self.bv = np.array(data["bv"])

    def train_step(self, states, policies, values, lr=1e-3):
        # Very simple SGD
        # Backward Pass
        
        x_flat = states.reshape(states.shape[0], -1)
        
        # Forward
        z1 = np.dot(x_flat, self.W1) + self.b1
        h1 = np.maximum(0, z1)
        
        p_logits = np.dot(h1, self.Wp) + self.bp
        v_pred = np.tanh(np.dot(h1, self.Wv) + self.bv)
        
        # Loss Gradients
        # MSE for Value: L = 0.5(v - target)^2 -> dL/dv = (v - target)
        # Tanh derivative: 1 - v^2
        dL_dv = (v_pred - values)
        dv_dz = (1 - v_pred**2)
        d_v = dL_dv * dv_dz
        
        # Cross Entropy for Policy: L = -sum(target * log(softmax(logits)))
        # Gradient wrt logits = softmax(logits) - target
        # Softmax
        exp_p = np.exp(p_logits - np.max(p_logits, axis=1, keepdims=True))
        probs = exp_p / np.sum(exp_p, axis=1, keepdims=True)
        d_p = (probs - policies)
        
        # Backprop
        # Wv
        self.Wv -= lr * np.dot(h1.T, d_v)
        self.bv -= lr * np.sum(d_v, axis=0)
        
        # Wp
        self.Wp -= lr * np.dot(h1.T, d_p)
        self.bp -= lr * np.sum(d_p, axis=0)
        
        # Hidden
        # dL/dh1 = dL/dp * Wp.T + dL/dv * Wv.T
        d_h1 = np.dot(d_p, self.Wp.T) + np.dot(d_v, self.Wv.T)
        # ReLU deriv
        d_z1 = d_h1 * (z1 > 0)
        
        self.W1 -= lr * np.dot(x_flat.T, d_z1)
        self.b1 -= lr * np.sum(d_z1, axis=0)
        
        loss = np.mean((v_pred - values)**2) - np.mean(np.sum(policies * np.log(probs + 1e-8), axis=1))
        return loss

# Shim for compatibility
AlphaZeroNet = TinyAlphaZero
