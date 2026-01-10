import sys
import os

# Ensure parent directory is in path to import flaw logic
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Add DLL path for MinGW dependencies
try:
    os.add_dll_directory(r"C:\Users\Administrator\Downloads\winlibs-x86_64-posix-seh-gcc-15.1.0-mingw-w64msvcrt-13.0.0-r4\mingw64\bin")
except AttributeError:
    pass

from flask import Flask, request, jsonify, render_template
from ai.adaptive_controller import PlayerProfile, AdaptiveFlaw
from ai.tournament_manager import TournamentManager
import json
import os
import flaw_core as fc

app = Flask(__name__, static_folder="static", template_folder="templates")

# Initialize profile and adaptive engine
profile = PlayerProfile.load()
adaptive = AdaptiveFlaw(profile)

@app.route("/")
def index():
    return render_template("layout.html")

@app.route("/reset", methods=["POST"])
def reset_board():
    adaptive.load_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    return jsonify({"status": "ok", "rating": profile.rating})

@app.route("/move", methods=["POST"])
def make_move():
    data = request.get_json()
    move = data.get("move", "") # e.g. "e2e4"
    if len(move) == 4:
        f_file = ord(move[0]) - 97
        f_rank = int(move[1]) - 1
        t_file = ord(move[2]) - 97
        t_rank = int(move[3]) - 1
        
        f = f_rank * 8 + f_file
        t = t_rank * 8 + t_file
        
        try:
            adaptive.engine.board.make_move(fc.Move(f, t, fc.Piece.EMPTY))
            return jsonify({"status": "ok"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400
            
    return jsonify({"status": "error", "message": "Invalid move format"}), 400

@app.route("/bestmove", methods=["GET"])
def bestmove():
    try:
        mv, score = adaptive.best_move()
        if not mv:
            # Check for game over and update rating
            if adaptive.engine.board.is_game_over():
                res = adaptive.engine.board.get_result()
                # If engine is white and get_result is 1, engine won. 
                # If player is black, player lost (score 0).
                # adaptive.profile.update_rating(1500 + adaptive.engine.depth * 100, player_score)
                # This is a bit complex for a single route; normally handled after game end POST.
                pass
            return jsonify({"bestmove": None})
            
        f = mv.from_sq
        t = mv.to_sq
        
        f_file = f % 8
        f_rank = f // 8 
        t_file = t % 8
        t_rank = t // 8
        
        from_sq_str = chr(f_file + 97) + str(f_rank + 1)
        to_sq_str = chr(t_file + 97) + str(t_rank + 1)
        
        return jsonify({
            "bestmove": from_sq_str + to_sq_str, 
            "score": score,
            "depth": adaptive.engine.depth,
            "alpha": adaptive.hybrid.alpha
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/leaderboard")
def leaderboard():
    lb_path = os.path.join(parent_dir, "leaderboard.json")
    if not os.path.exists(lb_path):
        # Create a dummy leaderboard if none exists
        dummy = {"Flaw (Default)": 1500, profile.name: profile.rating}
        with open(lb_path, "w") as f:
            json.dump(dummy, f)
            
    with open(lb_path, "r") as f:
        data = json.load(f)
    
    sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
    return render_template("leaderboard.html", leaders=sorted_data)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
