import flaw_core as fc
try:
    from ai.neural_core import IntentNet, evaluate_context
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("Warning: torch not found. HybridEvaluator will use C++ score only.")

class HybridEvaluator:
    def __init__(self, alpha=0.3, model_path="models/intent_net.pt"):
        self.alpha = alpha
        if TORCH_AVAILABLE:
            try:
                self.model = IntentNet()
                # Use map_location='cpu' to be safe
                self.model.load_state_dict(torch.load(model_path, map_location="cpu"))
                self.model.eval()
                self.neural_active = True
            except FileNotFoundError:
                print(f"Model file {model_path} not found. Using random/untrained valid net or disabling.")
                # For safety, if model missing, maybe just disable neural part
                self.neural_active = False 
                # Or keep it initialized random if that's preferred for testing?
                # User prompted "learns from... logs", so random is bad. Disabling is safer.
        else:
            self.neural_active = False

    def evaluate(self, board, ctx):
        """Blend C++ and neural evaluations."""
        cpp_score = fc.Evaluator_evaluate(board)  # exposed C++ function
        
        neural_score = 0
        if self.neural_active:
             neural_score = evaluate_context(self.model, ctx) * 1000  # rescale
        
        # If neural is not active, alpha should be effectively 0? 
        # Or just return cpp_score?
        if not self.neural_active:
            return cpp_score
            
        hybrid_score = (1 - self.alpha) * cpp_score + self.alpha * neural_score
        return hybrid_score
