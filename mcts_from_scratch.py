# mcts_from_scratch.py
import math
import random
import time
from typing import Optional, List, Tuple
from board import GomokuBoard
from player import Player

Move = Tuple[int, int]

class MCTSNode:
    def __init__(self, board: GomokuBoard, parent: Optional['MCTSNode'] = None, move: Optional[Move] = None):
        self.board = board.copy()
        self.parent = parent
        self.move = move
        self.visits = 0
        self.wins = 0.0
        self.untried_moves = board.get_legal_moves()
        self.children = []

    def is_fully_expanded(self) -> bool:
        return len(self.untried_moves) == 0

    def best_child(self, exploration_constant: float = 1.414) -> 'MCTSNode':
        log_visits = math.log(self.visits)
        def ucb_score(child):
            win_rate = child.wins / child.visits if child.visits > 0 else 0.0
            exploration = exploration_constant * math.sqrt(log_visits / child.visits)
            return win_rate + exploration
        return max(self.children, key=ucb_score)

    def expand(self) -> 'MCTSNode':
        move = random.choice(self.untried_moves)
        self.untried_moves.remove(move)
        new_board = self.board.copy()
        new_board.make_move(move)
        child = MCTSNode(new_board, parent=self, move=move)
        self.children.append(child)
        return child

    def rollout(self) -> float:
        board = self.board.copy()
        current_player = board.current_player
        while not board.is_game_over():
            legal = board.get_legal_moves()
            if not legal:
                break
            move = random.choice(legal)
            board.make_move(move)
        winner = board.get_winner()
        if winner == 0:
            return 0.5
        return 1.0 if winner == current_player else 0.0

    def backpropagate(self, result: float):
        self.visits += 1
        self.wins += result
        if self.parent:
            self.parent.backpropagate(1.0 - result)


class MCTSPlayer(Player):
    def __init__(self, player_id: int, num_simulations: int = 500, time_limit: Optional[float] = None):
        # 不调用父类构造函数，直接存储 player_id
        self.player_id = player_id
        self.num_simulations = num_simulations
        self.time_limit = time_limit

    def get_move(self, board: GomokuBoard) -> Move:
        root = MCTSNode(board)
        start = time.time()
        sim_count = 0

        while True:
            if self.time_limit and (time.time() - start) >= self.time_limit:
                break
            if self.num_simulations and sim_count >= self.num_simulations:
                break

            node = root
            # 选择
            while node.is_fully_expanded() and node.children:
                node = node.best_child()
            # 扩展
            if not node.is_fully_expanded() and not node.board.is_game_over():
                node = node.expand()
            # 模拟
            result = node.rollout()
            # 回溯
            node.backpropagate(result)
            sim_count += 1

        if not root.children:
            legal = board.get_legal_moves()
            return random.choice(legal) if legal else None
        best_child = max(root.children, key=lambda c: c.visits)
        return best_child.move