import os
import sys

# Windows DLL path
try:
    os.add_dll_directory(r"C:\Users\Administrator\Downloads\winlibs-x86_64-posix-seh-gcc-15.1.0-mingw-w64msvcrt-13.0.0-r4\mingw64\bin")
except AttributeError:
    pass

from ai.tournament_manager import TournamentManager

if __name__ == "__main__":
    print("Welcome to Flaw Tournament Mode!")
    participants = ["Grandmaster", "Alice", "Bob", "Charlie", "Flaw-v1"]
    
    print(f"Running round-robin tournament for: {', '.join(participants)}")
    tm = TournamentManager(participants)
    ratings = tm.run()
    
    print("\n--- Final Leaderboard ---")
    for name, rating in sorted(ratings.items(), key=lambda x: x[1], reverse=True):
        print(f"{name:15}: {rating:.0f}")
        
    print(f"\nResults saved to tournament_results.json and leaderboard.json")
