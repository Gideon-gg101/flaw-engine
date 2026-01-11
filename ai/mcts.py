import numpy as np
import math
import random
import chess
from .neural_core import TinyAlphaZero

class MCTSNode:
    def __init__(self, prior, parent=None):
        self.parent = parent
        self.children = {}  # move -> MCTSNode
        self.visit_count = 0
        self.value_sum = 0
        self.prior = prior

    @property
    def value(self):
        if self.visit_count == 0:
            return 0
        return self.value_sum / self.visit_count

    def select(self, c_puct):
        return max(self.children.items(),
                   key=lambda item: item[1].get_score(c_puct))

    def get_score(self, c_puct):
        u_score = c_puct * self.prior * math.sqrt(self.parent.visit_count + 1e-8) / (1 + self.visit_count)
        return self.value + u_score

class MCTSGame:
    def __init__(self, board=None):
        self.board = board if board else chess.Board()

    def legal_moves(self):
        return list(self.board.legal_moves)

    def make_move(self, move):
        self.board.push(move)

    def is_game_over(self):
        return self.board.is_game_over()

    def result(self):
        res = self.board.result()
        if res == "1-0": return 1.0
        if res == "0-1": return -1.0
        return 0.0

    def clone(self):
        return MCTSGame(self.board.copy())

    def to_tensor(self):
        # 13x8x8: 6 us, 6 them, 1 side
        planes = np.zeros((13, 8, 8), dtype=np.float32)
        us = self.board.turn
        
        for sq in range(64):
            piece = self.board.piece_at(sq)
            if piece:
                # 0-5 for our pieces, 6-11 for theirs
                p_type = piece.piece_type - 1
                if piece.color == us:
                    p_idx = p_type
                else:
                    p_idx = p_type + 6
                
                rank, file = divmod(sq, 8)
                planes[p_idx, rank, file] = 1.0
        
        if us == chess.BLACK:
            planes[12].fill(1.0)
            
        return planes

def mcts_search(game, net, sims=50, c_puct=1.4):
    root = MCTSNode(prior=0)
    
    # 1. Expand root
    policy, value = net.forward(game.to_tensor().flatten())
    policy = policy.flatten()
    value = float(value)
    legal_moves = game.legal_moves()
    
    if not legal_moves:
        return None

    total_p = 0
    move_probs = []
    for m in legal_moves:
        idx = m.from_square * 64 + m.to_square
        p = math.exp(policy[idx])
        move_probs.append((m, p))
        total_p += p
    
    for m, p in move_probs:
        root.children[m] = MCTSNode(prior=p/total_p, parent=root)

    for _ in range(sims):
        node = root
        scratch_game = game.clone()
        
        # Selection
        while node.children:
            move, node = node.select(c_puct)
            scratch_game.make_move(move)
        
        # Expansion and Evaluation
        if not scratch_game.is_game_over():
            policy, value = net.forward(scratch_game.to_tensor().flatten())
            policy = policy.flatten()
            value = float(value)
            legal_moves = scratch_game.legal_moves()
            
            total_p = 0
            move_probs = []
            for m in legal_moves:
                idx = m.from_square * 64 + m.to_square
                p = math.exp(policy[idx])
                move_probs.append((m, p))
                total_p += p
            
            for m, p in move_probs:
                node.children[m] = MCTSNode(prior=p/total_p, parent=node)
        else:
            value = scratch_game.result()
            # If it's black's turn, the result is from white's perspective,
            # but MCTS usually wants perspective of the side-to-move.
            # However, AZ convention is the value is relative to the current player.
            if scratch_game.board.turn == chess.BLACK:
                value = -value

        # Backup
        while node:
            node.visit_count += 1
            node.value_sum += value
            value = -value
            node = node.parent
            
    return root
