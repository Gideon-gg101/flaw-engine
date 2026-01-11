import os
os.add_dll_directory(r"C:\Users\Administrator\Downloads\winlibs-x86_64-posix-seh-gcc-15.1.0-mingw-w64msvcrt-13.0.0-r4\mingw64\bin")
import flaw_core as fc

# Test 1: Check promotion moves are generated
print("=== Testing Promotion Move Generation ===")
b = fc.Board()
b.load_fen("8/P7/8/8/8/8/8/k6K w - - 0 1")
moves = b.generate_moves()
print(f"Total legal moves: {len(moves)}")
for m in moves:
    if m.from_sq == 48:  # a7 square
        move_str = f"{chr(m.from_sq%8+97)}{m.from_sq//8+1}{chr(m.to_sq%8+97)}{m.to_sq//8+1}"
        print(f"  {move_str} promotion={m.promotion}")

# Test 2: Execute a promotion
print("\n=== Testing Promotion Execution ===")
b2 = fc.Board()
b2.load_fen("8/P7/8/8/8/8/8/k6K w - - 0 1")
print(f"Before: {b2.to_fen()}")
# Find the correct promotion move
prom_move = None
for m in b2.generate_moves():
    if m.from_sq == 48 and m.to_sq == 56:
        prom_move = m
        break
if prom_move:
    print(f"Executing move with promotion={prom_move.promotion}")
    b2.make_move(prom_move)
    print(f"After:  {b2.to_fen()}")
else:
    print("ERROR: Promotion move not found!")

# Test 3: Castling
print("\n=== Testing Castling Execution ===")
b3 = fc.Board()
b3.load_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
print(f"Before: {b3.to_fen()}")
castle_move = None
for m in b3.generate_moves():
    if m.from_sq == 4 and m.to_sq == 6:  # e1g1
        castle_move = m
        break
if castle_move:
    print(f"Executing castling e1g1")
    b3.make_move(castle_move)
    print(f"After:  {b3.to_fen()}")
