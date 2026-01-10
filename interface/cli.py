from ai.search_controller import FlawEngine
import flaw_core as fc
import sys

def run():
    engine = FlawEngine(depth=2)
    start = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    engine.load_fen(start)
    
    print("Flaw Engine CLI")
    print("Initial position loaded.")
    
    while True:
        try:
            mv, score = engine.best_move()
            if mv:
                print(f"Best move: {mv.from_sq}->{mv.to_sq}, eval {score}")
            else:
                print("No legal moves found (mate or stalemate).")
                
            cmd = input("Make move (from to) or q to quit: ")
            if cmd == "q": break
            
            parts = cmd.split()
            if len(parts) >= 2:
                f, t = int(parts[0]), int(parts[1])
                engine.board.make_move(fc.Move(f, t, fc.Piece.EMPTY))
                print("Move made.")
            else:
                print("Invalid input format.")
                
        except Exception as e:
            print("Error:", e)
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    # Ensure current directory is in path to find flaw_core
    sys.path.append('.') 
    run()
