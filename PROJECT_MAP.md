# Flaw Engine - Project File Map

A comprehensive guide to the hybrid C++/Python chess engine ecosystem.

## 📁 Core Engine (C++ / `core/`)
Compiled via `CMake` into `flaw_core.pyd`.

- [board.h](file:///c:/Users/Administrator/Desktop/Chess2.0/Engines2.0/flaw/core/board.h) / [.cpp](file:///c:/Users/Administrator/Desktop/Chess2.0/Engines2.0/flaw/core/board.cpp): Bitboard representation, Zobrist hashing, FEN IO, game state.
- [movegen.h](file:///c:/Users/Administrator/Desktop/Chess2.0/Engines2.0/flaw/core/movegen.h) / [.cpp](file:///c:/Users/Administrator/Desktop/Chess2.0/Engines2.0/flaw/core/movegen.cpp): Legal move generation logic.
- [evaluator.h](file:///c:/Users/Administrator/Desktop/Chess2.0/Engines2.0/flaw/core/evaluator.h) / [.cpp](file:///c:/Users/Administrator/Desktop/Chess2.0/Engines2.0/flaw/core/evaluator.cpp): Static material evaluation.
- [dis.h](file:///c:/Users/Administrator/Desktop/Chess2.0/Engines2.0/flaw/core/dis.h) / [.cpp](file:///c:/Users/Administrator/Desktop/Chess2.0/Engines2.0/flaw/core/dis.cpp): Direct Intent Search (Minimax + AlphaBeta).
- [transposition.h](file:///c:/Users/Administrator/Desktop/Chess2.0/Engines2.0/flaw/core/transposition.h): Thread-safe caching for search results.
- [flaw_core.cpp](file:///c:/Users/Administrator/Desktop/Chess2.0/Engines2.0/flaw/core/flaw_core.cpp): PyBind11 bindings with GIL release for threading.

## 📁 AI Logic (Python / `ai/`)
Orchestration and learning.

- [search_controller.py](file:///c:/Users/Administrator/Desktop/Chess2.0/Engines2.0/flaw/ai/search_controller.py): Multithreaded Python search manager.
- [neural_core.py](file:///c:/Users/Administrator/Desktop/Chess2.0/Engines2.0/flaw/ai/neural_core.py): PyTorch `IntentNet` and training helpers.
- [hybrid_evaluator.py](file:///c:/Users/Administrator/Desktop/Chess2.0/Engines2.0/flaw/ai/hybrid_evaluator.py): Blending C++ and Neural scores.
- [selfplay_trainer.py](file:///c:/Users/Administrator/Desktop/Chess2.0/Engines2.0/flaw/ai/selfplay_trainer.py): Basic heuristic weight update loop.
- [reinforcement_trainer.py](file:///c:/Users/Administrator/Desktop/Chess2.0/Engines2.0/flaw/ai/reinforcement_trainer.py): Full Value-Regression RL pipeline.
- [adaptive_controller.py](file:///c:/Users/Administrator/Desktop/Chess2.0/Engines2.0/flaw/ai/adaptive_controller.py): Difficulty scaling based on user Elo.
- [elo_benchmark.py](file:///c:/Users/Administrator/Desktop/Chess2.0/Engines2.0/flaw/ai/elo_benchmark.py): Automated strength measurement system.
- [tournament_manager.py](file:///c:/Users/Administrator/Desktop/Chess2.0/Engines2.0/flaw/ai/tournament_manager.py): Tournament pairing and leaderboard updates.

## 📁 Interfaces (`interface/` & `flaw_web/`)
How you interact with Flaw.

- [uci_adapter.py](file:///c:/Users/Administrator/Desktop/Chess2.0/Engines2.0/flaw/interface/uci_adapter.py): standard UCI protocol for GUIs (Arena, CuteChess).
- [cli.py](file:///c:/Users/Administrator/Desktop/Chess2.0/Engines2.0/flaw/interface/cli.py): simple command-line interface.
- [app.py](file:///c:/Users/Administrator/Desktop/Chess2.0/Engines2.0/flaw/flaw_web/app.py): Flask backend for web UI.
- [templates/layout.html](file:///c:/Users/Administrator/Desktop/Chess2.0/Engines2.0/flaw/flaw_web/templates/layout.html): Dark-mode web board.
- [templates/leaderboard.html](file:///c:/Users/Administrator/Desktop/Chess2.0/Engines2.0/flaw/flaw_web/templates/leaderboard.html): Tournament dashboard.

## 🚀 Entry Points
- `python flaw_web/app.py`: Play in browser at localhost:5000.
- `python main_tournament.py`: Run a simulated local tournament.
- `python benchmark.py`: Test search performance.
- `python -m interface.uci_adapter`: Connect to a Chess GUI.
