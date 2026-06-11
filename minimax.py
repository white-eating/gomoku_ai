import math
import random
import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple, Set
import numpy as np
from board import Board
from player import Player

Move = Tuple[int, int]
EvalFunc = Callable[[Board, int], float]

EXACT = "EXACT"
LOWER_BOUND = "LOWER"
UPPER_BOUND = "UPPER"

@dataclass
class SearchStats:
    """搜索统计信息，包含置换表命中率等。"""
    nodes: int = 0
    cutoffs: int = 0
    completed_depth: int = 0
    elapsed: float = 0.0
    timed_out: bool = False
    tt_lookups: int = 0
    tt_hits: int = 0
    tt_stores: int = 0

    @property
    def tt_hit_rate(self) -> float:
        if self.tt_lookups == 0:
            return 0.0
        return self.tt_hits / self.tt_lookups


@dataclass
class TranspositionEntry:
    """置换表条目。"""
    depth: int
    value: float
    flag: str          # EXACT / LOWER_BOUND / UPPER_BOUND
    best_move: Optional[Move]

class SearchTimeout(Exception):
    pass


class ZobristHasher:
    """Zobrist 哈希器，为局面生成 64 位随机数，用于快速索引置换表。"""

    def __init__(self, size: int, seed: int = 20260608):
        self.size = size
        rng = random.Random(seed + size * 131)
        # shape: (size, size, 3) —— 棋子类型 0/1/2
        self.piece_keys = np.array(
            [[[0, rng.getrandbits(64), rng.getrandbits(64)] for _ in range(size)]
             for _ in range(size)],
            dtype=np.uint64,
        )
        self.player_keys = {1: rng.getrandbits(64), 2: rng.getrandbits(64)}
        self.cache_name = f"_zobrist_cache_{seed}_{size}"

    def hash_board(self, board: Board) -> int:
        cached = getattr(board, self.cache_name, None)
        if cached is not None:
            return cached
        selected = np.take_along_axis(self.piece_keys, board.board[:, :, None], axis=2).reshape(-1)
        h = int(np.bitwise_xor.reduce(selected, dtype=np.uint64))
        h ^= self.player_keys.get(board.current_player, 0)
        setattr(board, self.cache_name, h)
        return h


class TranspositionTable:
    """基于 Zobrist 哈希的字典缓存。"""

    def __init__(self, board_size: int, seed: int = 20260608):
        self.hasher = ZobristHasher(board_size, seed)
        self.table: Dict[Tuple[int, int], TranspositionEntry] = {}

    def make_key(self, board: Board, root_player: int) -> Tuple[int, int]:
        return self.hasher.hash_board(board), root_player

    def get(self, board: Board, root_player: int) -> Optional[TranspositionEntry]:
        return self.table.get(self.make_key(board, root_player))

    def store(self, board: Board, root_player: int, entry: TranspositionEntry) -> None:
        key = self.make_key(board, root_player)
        old = self.table.get(key)
        if old is None or entry.depth >= old.depth:
            self.table[key] = entry

    def __len__(self) -> int:
        return len(self.table)


# ---------- 井字棋评估 ----------
def evaluate_tic_tac_toe(board: Board, player: int) -> float:
    winner = board.get_winner()
    if winner == player: return 1.0
    if winner == 0: return 0.0
    if winner is not None: return -1.0
    return 0.0

def heuristic_tic_tac_toe(board: Board, player: int) -> float:
    if board.is_game_over(): return evaluate_tic_tac_toe(board, player)
    score = 0
    center = board.size // 2
    for r in range(board.size):
        for c in range(board.size):
            piece = int(board.board[r, c])
            if piece == player:
                score += 5 if (r, c) == (center, center) else 3 if r in (0, board.size - 1) and c in (0, board.size - 1) else 1
            elif piece != 0:
                score -= 5 if (r, c) == (center, center) else 3 if r in (0, board.size - 1) and c in (0, board.size - 1) else 1
    return float(score)

# ---------- 五子棋高级评估函数 ----------
def evaluate_gomoku(board: Board, player: int) -> float:
    """
    五子棋局面评估：基于棋型分数，攻防平衡 = 己方分 - 对方分 × 防守权重。
    """
    winner = board.get_winner()
    if winner == player: return 100_000_000.0
    if winner == 0: return 0.0
    if winner is not None: return -100_000_000.0

    opponent = 3 - player
    my_score = _advanced_shape_score(board, player)
    opp_score = _advanced_shape_score(board, opponent)

    DEFENSE_WEIGHT = 1.1
    final_score = my_score - (opp_score * DEFENSE_WEIGHT)

    center = board.size // 2
    pos_score = 0
    for r in range(board.size):
        for c in range(board.size):
            if board.board[r, c] == player:
                dist = abs(r - center) + abs(c - center)
                pos_score += max(0, 10 - dist)
            elif board.board[r, c] == opponent:
                dist = abs(r - center) + abs(c - center)
                pos_score -= max(0, 10 - dist)
    final_score += pos_score

    return float(final_score)


def _advanced_shape_score(board: Board, player: int) -> int:
    size = board.size
    b = board.board
    total_score = 0
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

    SHAPE_SCORES = {
        'FIVE': 1000000,
        'LIVE_FOUR': 100000,
        'RUSH_FOUR': 10000,
        'LIVE_THREE': 3000,
        'SLEEP_THREE': 300,
        'LIVE_TWO': 100,
        'SLEEP_TWO': 30,
    }

    for r in range(size):
        for c in range(size):
            if b[r, c] != player:
                continue
            for d_idx, (dr, dc) in enumerate(directions):
                pr, pc = r - dr, c - dc
                if 0 <= pr < size and 0 <= pc < size and b[pr, pc] == player:
                    continue

                count = 1
                block_ends = 0

                for step in range(1, 5):
                    nr, nc = r + dr * step, c + dc * step
                    if not (0 <= nr < size and 0 <= nc < size):
                        block_ends += 1
                        break
                    if b[nr, nc] == player:
                        count += 1
                    elif b[nr, nc] != 0:
                        block_ends += 1
                        break
                    else:
                        break

                if 0 <= pr < size and 0 <= pc < size:
                    if b[pr, pc] != 0:
                        block_ends += 1
                else:
                    block_ends += 1

                if count >= 5:
                    total_score += SHAPE_SCORES['FIVE']
                elif count == 4:
                    if block_ends == 0:
                        total_score += SHAPE_SCORES['LIVE_FOUR']
                    elif block_ends == 1:
                        total_score += SHAPE_SCORES['RUSH_FOUR']
                elif count == 3:
                    if block_ends == 0:
                        total_score += SHAPE_SCORES['LIVE_THREE']
                    elif block_ends == 1:
                        total_score += SHAPE_SCORES['SLEEP_THREE']
                elif count == 2:
                    if block_ends == 0:
                        total_score += SHAPE_SCORES['LIVE_TWO']
                    elif block_ends == 1:
                        total_score += SHAPE_SCORES['SLEEP_TWO']
    return total_score


# ---------- 威胁检测 ----------
def _find_opponent_threats(board: Board, opponent: int):
    """
    检测对手的所有直接威胁。
    返回:
      direct_win_moves: List[Move]  对手一步必胜的空位（五个连续位置内四子一空）
      open_three_defends: Set[Move] 对手活三的空位（四个连续位置内三子一空且两端空）
    """
    size = board.size
    b = board.board
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

    direct_win_moves = set()
    open_three_defends = set()

    for r in range(size):
        for c in range(size):
            if b[r, c] != 0:
                continue
            for dr, dc in directions:
                # ---- 检查长度为5的窗口（一步杀） ----
                for start_offset in range(-4, 1):
                    cells = []
                    valid = True
                    for k in range(5):
                        nr = r + dr * (k + start_offset)
                        nc = c + dc * (k + start_offset)
                        if not (0 <= nr < size and 0 <= nc < size):
                            valid = False
                            break
                        cells.append((nr, nc))
                    if not valid:
                        continue
                    opp_count = 0
                    empty_count = 0
                    for (nr, nc) in cells:
                        if b[nr, nc] == opponent:
                            opp_count += 1
                        elif b[nr, nc] == 0:
                            empty_count += 1
                    if opp_count == 4 and empty_count == 1:
                        direct_win_moves.add((r, c))

                # ---- 检查长度为4的窗口（活三） ----
                for start_offset in range(-3, 1):
                    cells = []
                    valid = True
                    for k in range(4):
                        nr = r + dr * (k + start_offset)
                        nc = c + dc * (k + start_offset)
                        if not (0 <= nr < size and 0 <= nc < size):
                            valid = False
                            break
                        cells.append((nr, nc))
                    if not valid:
                        continue
                    opp_count = 0
                    empty_count = 0
                    for (nr, nc) in cells:
                        if b[nr, nc] == opponent:
                            opp_count += 1
                        elif b[nr, nc] == 0:
                            empty_count += 1
                    if opp_count == 3 and empty_count == 1:
                        left_r = r + dr * (start_offset - 1)
                        left_c = c + dc * (start_offset - 1)
                        right_r = r + dr * (start_offset + 4)
                        right_c = c + dc * (start_offset + 4)
                        left_empty = (0 <= left_r < size and 0 <= left_c < size and b[left_r, left_c] == 0)
                        right_empty = (0 <= right_r < size and 0 <= right_c < size and b[right_r, right_c] == 0)
                        if left_empty and right_empty:
                            open_three_defends.add((r, c))

    return {
        'direct_win_moves': list(direct_win_moves),
        'open_three_defends': open_three_defends,
    }


# ---------- 候选走法 ----------
def _quick_static_score(board: Board, move: Move, player: int) -> float:
    size = board.size
    r, c = move
    center = size // 2
    dist_score = max(0, 10 - (abs(r - center) + abs(c - center)))
    neighbours = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < size and 0 <= nc < size and board.board[nr, nc] != 0:
                neighbours += 1
    return dist_score + neighbours * 2


def _candidate_moves(board: Board, player: int, eval_func: EvalFunc,
                     max_moves: Optional[int] = None,
                     preferred_move: Optional[Move] = None) -> List[Move]:
    legal_moves = board.get_legal_moves()
    if not legal_moves:
        return []
    if board.size <= 3:
        return legal_moves

    occupied = np.argwhere(board.board != 0)
    if len(occupied) == 0:
        center = board.size // 2
        if (center, center) in legal_moves:
            return [(center, center)]
        return legal_moves[:1]

    # ----- 正常局面：生成邻近点 + 威胁防守点 -----
    legal_set = set(legal_moves)
    near = set()
    radius = 2
    for r, c in occupied:
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = int(r) + dr, int(c) + dc
                if (nr, nc) in legal_set:
                    near.add((nr, nc))

    opponent = 3 - player
    threats = _find_opponent_threats(board, opponent)
    direct_wins = set(threats['direct_win_moves'])
    open_threes = threats['open_three_defends']
    critical = direct_wins | open_threes
    near.update(critical)

    moves = list(near) if near else legal_moves

    # 排序：关键防守点优先，再按快速静态评分
    key_moves = []
    other_moves = []
    for m in moves:
        if m in critical:
            key_moves.append(m)
        else:
            other_moves.append(m)

    key_moves.sort(key=lambda m: _quick_static_score(board, m, player), reverse=True)
    other_moves.sort(key=lambda m: _quick_static_score(board, m, player), reverse=True)
    moves = key_moves + other_moves

    if preferred_move is not None and preferred_move in moves:
        moves.remove(preferred_move)
        moves.insert(0, preferred_move)

    if max_moves is not None and len(moves) > max_moves:
        moves = moves[:max_moves]
    return moves


# ---------- 搜索算法 ----------
def minimax(board: Board, depth: int, maximizing_player: bool, player: int,
            eval_func: EvalFunc, stats: Optional[SearchStats] = None,
            deadline: Optional[float] = None) -> Tuple[float, Optional[Move]]:
    if deadline is not None and time.perf_counter() >= deadline:
        raise SearchTimeout
    if stats is not None:
        stats.nodes += 1
    if board.is_game_over() or depth == 0:
        return eval_func(board, player), None

    legal_moves = _candidate_moves(board, player, eval_func, max_moves=None)
    if not legal_moves:
        return eval_func(board, player), None

    best_move = None
    if maximizing_player:
        max_score = -math.inf
        for move in legal_moves:
            new_board = board.copy()
            new_board.make_move(move)
            score, _ = minimax(new_board, depth - 1, False, player, eval_func, stats, deadline)
            if score > max_score:
                max_score, best_move = score, move
        return max_score, best_move
    else:
        min_score = math.inf
        for move in legal_moves:
            new_board = board.copy()
            new_board.make_move(move)
            score, _ = minimax(new_board, depth - 1, True, player, eval_func, stats, deadline)
            if score < min_score:
                min_score, best_move = score, move
        return min_score, best_move


def alpha_beta(board: Board, depth: int, alpha: float, beta: float,
               maximizing_player: bool, player: int, eval_func: EvalFunc,
               stats: Optional[SearchStats] = None, deadline: Optional[float] = None,
               max_moves: Optional[int] = None,
               transposition_table: Optional[TranspositionTable] = None):
    """Alpha‑Beta 剪枝，集成置换表加速。"""
    if deadline is not None and time.perf_counter() >= deadline:
        raise SearchTimeout
    if stats is not None:
        stats.nodes += 1

    original_alpha, original_beta = alpha, beta
    preferred_move = None

    if transposition_table is not None:
        if stats is not None:
            stats.tt_lookups += 1
        entry = transposition_table.get(board, player)
        if entry is not None:
            preferred_move = entry.best_move
            if entry.depth >= depth:
                if entry.flag == EXACT:
                    if stats is not None:
                        stats.tt_hits += 1
                    return entry.value, entry.best_move
                if entry.flag == LOWER_BOUND:
                    alpha = max(alpha, entry.value)
                elif entry.flag == UPPER_BOUND:
                    beta = min(beta, entry.value)
                if alpha >= beta:
                    if stats is not None:
                        stats.tt_hits += 1
                    return entry.value, entry.best_move

    if board.is_game_over() or depth == 0:
        value = eval_func(board, player)
        if transposition_table is not None:
            transposition_table.store(board, player, TranspositionEntry(depth, value, EXACT, None))
            if stats is not None:
                stats.tt_stores += 1
        return value, None

    legal_moves = _candidate_moves(board, player, eval_func, max_moves=max_moves, preferred_move=preferred_move)
    if not legal_moves:
        value = eval_func(board, player)
        if transposition_table is not None:
            transposition_table.store(board, player, TranspositionEntry(depth, value, EXACT, None))
            if stats is not None:
                stats.tt_stores += 1
        return value, None

    best_move = None
    if maximizing_player:
        value = -math.inf
        for move in legal_moves:
            new_board = board.copy()
            new_board.make_move(move)
            score, _ = alpha_beta(new_board, depth - 1, alpha, beta, False, player, eval_func,
                                  stats, deadline, max_moves, transposition_table)
            if score > value:
                value, best_move = score, move
            alpha = max(alpha, value)
            if alpha >= beta:
                if stats is not None:
                    stats.cutoffs += 1
                break
    else:
        value = math.inf
        for move in legal_moves:
            new_board = board.copy()
            new_board.make_move(move)
            score, _ = alpha_beta(new_board, depth - 1, alpha, beta, True, player, eval_func,
                                  stats, deadline, max_moves, transposition_table)
            if score < value:
                value = score
                best_move = move
            beta = min(beta, value)
            if beta <= alpha:
                if stats is not None:
                    stats.cutoffs += 1
                break

    if transposition_table is not None:
        if value <= original_alpha:
            flag = UPPER_BOUND
        elif value >= original_beta:
            flag = LOWER_BOUND
        else:
            flag = EXACT
        transposition_table.store(board, player, TranspositionEntry(depth, value, flag, best_move))
        if stats is not None:
            stats.tt_stores += 1

    return value, best_move


def iterative_deepening_search(board: Board, player: int, eval_func: EvalFunc,
                               time_limit: float = 2.0, max_depth: int = 10,
                               use_alpha_beta: bool = True,
                               max_moves: Optional[int] = 30,
                               use_transposition_table: bool = True):
    """迭代加深搜索，超时返回当前最佳走法。"""
    start = time.perf_counter()
    deadline = start + time_limit
    best_move = None
    aggregate = SearchStats()
    tt = TranspositionTable(board.size) if use_transposition_table and use_alpha_beta else None

    fallback = _candidate_moves(board, player, eval_func, max_moves=max_moves)
    if fallback:
        best_move = fallback[0]

    for depth in range(1, max_depth + 1):
        stats = SearchStats()
        try:
            if use_alpha_beta:
                score, move = alpha_beta(board, depth, -math.inf, math.inf, True, player, eval_func,
                                         stats=stats, deadline=deadline, max_moves=max_moves,
                                         transposition_table=tt)
            else:
                score, move = minimax(board, depth, True, player, eval_func, stats=stats, deadline=deadline)
            aggregate.nodes += stats.nodes
            aggregate.cutoffs += stats.cutoffs
            aggregate.tt_lookups += stats.tt_lookups
            aggregate.tt_hits += stats.tt_hits
            aggregate.tt_stores += stats.tt_stores
            aggregate.completed_depth = depth
            if move is not None:
                best_move = move
        except SearchTimeout:
            aggregate.timed_out = True
            break
        if time.perf_counter() >= deadline:
            aggregate.timed_out = True
            break

    aggregate.elapsed = time.perf_counter() - start
    return 0.0, best_move, aggregate


def timed_alpha_beta(board: Board, depth: int, player: int, eval_func: EvalFunc,
                     max_moves: Optional[int] = None,
                     use_transposition_table: bool = False):
    """运行一次 Alpha-Beta 并返回详细统计，用于实验对比。"""
    stats = SearchStats()
    tt = TranspositionTable(board.size) if use_transposition_table else None
    start = time.perf_counter()
    score, move = alpha_beta(
        board, depth, -math.inf, math.inf, True, player, eval_func,
        stats=stats, max_moves=max_moves, transposition_table=tt,
    )
    stats.elapsed = time.perf_counter() - start
    stats.completed_depth = depth
    return score, move, stats, len(tt) if tt is not None else 0


def compare_transposition_table_speed(board: Board, depth: int, player: int, eval_func: EvalFunc,
                                      max_moves: Optional[int] = 16):
    """对比无/有置换表时的搜索性能。"""
    base_score, base_move, base_stats, _ = timed_alpha_beta(
        board, depth, player, eval_func, max_moves=max_moves, use_transposition_table=False
    )
    tt_score, tt_move, tt_stats, tt_size = timed_alpha_beta(
        board, depth, player, eval_func, max_moves=max_moves, use_transposition_table=True
    )
    speedup = base_stats.elapsed / tt_stats.elapsed if tt_stats.elapsed > 0 else math.inf
    node_reduction = 1 - (tt_stats.nodes / base_stats.nodes) if base_stats.nodes else 0.0
    return {
        "same_score": base_score == tt_score,
        "same_move": base_move == tt_move,
        "without_tt": {
            "score": base_score,
            "move": base_move,
            "nodes": base_stats.nodes,
            "cutoffs": base_stats.cutoffs,
            "elapsed": base_stats.elapsed,
        },
        "with_tt": {
            "score": tt_score,
            "move": tt_move,
            "nodes": tt_stats.nodes,
            "cutoffs": tt_stats.cutoffs,
            "elapsed": tt_stats.elapsed,
            "tt_lookups": tt_stats.tt_lookups,
            "tt_hits": tt_stats.tt_hits,
            "tt_hit_rate": tt_stats.tt_hit_rate,
            "tt_stores": tt_stats.tt_stores,
            "tt_size": tt_size,
        },
        "speedup": speedup,
        "node_reduction": node_reduction,
    }


# ---------- AI 玩家 ----------
class MinimaxPlayer(Player):
    def __init__(self, player_id: int, depth: int = 9, use_alpha_beta: bool = True,
                 eval_func: Optional[EvalFunc] = None, iterative: bool = False,
                 time_limit: float = 2.0, max_moves: Optional[int] = None,
                 use_transposition_table: bool = True):
        self.player_id = player_id
        self.depth = depth
        self.use_alpha_beta = use_alpha_beta
        self.eval_func = eval_func if eval_func is not None else evaluate_tic_tac_toe
        self.iterative = iterative
        self.time_limit = time_limit
        self.max_moves = max_moves
        self.use_transposition_table = use_transposition_table
        self.last_stats: Optional[SearchStats] = None
        self.last_score: Optional[float] = None

    def get_move(self, board: Board) -> Move:
        # 1. 自己一步必胜
        for move in board.get_legal_moves():
            new_board = board.copy()
            new_board.make_move(move)
            if new_board.is_game_over() and new_board.get_winner() == self.player_id:
                return move

        opponent = 3 - self.player_id

        # 2. 对手威胁检测
        threats = _find_opponent_threats(board, opponent)
        direct_wins = threats['direct_win_moves']
        open_threes = threats['open_three_defends']

        # 2a. 对手一步杀（四连）
        if direct_wins:
            if len(direct_wins) == 1:
                return direct_wins[0]
            return board.get_legal_moves()[0]   # 多杀点，放弃防守

        # 2b. 对手活三
        if open_threes:
            defend_points = list(open_threes)
            if len(defend_points) <= 4:
                best_score = -math.inf
                best_move = defend_points[0]
                for move in defend_points:
                    new_board = board.copy()
                    new_board.make_move(move)
                    score, _ = alpha_beta(new_board, 2, -math.inf, math.inf,
                                          False, self.player_id, self.eval_func)
                    if score > best_score:
                        best_score = score
                        best_move = move
                return best_move
            else:
                return max(defend_points, key=lambda m: _quick_static_score(board, m, self.player_id))

        # 3. 正常搜索
        max_moves = self.max_moves
        if max_moves is None and board.size > 3:
            max_moves = 30

        if self.iterative:
            _, move, stats = iterative_deepening_search(
                board, self.player_id, self.eval_func,
                time_limit=self.time_limit, max_depth=self.depth,
                use_alpha_beta=self.use_alpha_beta, max_moves=max_moves,
                use_transposition_table=self.use_transposition_table,
            )
            self.last_stats = stats
            return move

        stats = SearchStats()
        if self.use_alpha_beta:
            tt = TranspositionTable(board.size) if self.use_transposition_table else None
            start = time.perf_counter()
            score, move = alpha_beta(board, self.depth, -math.inf, math.inf, True,
                                     self.player_id, self.eval_func, stats=stats,
                                     max_moves=max_moves, transposition_table=tt)
            stats.elapsed = time.perf_counter() - start
        else:
            start = time.perf_counter()
            score, move = minimax(board, self.depth, True, self.player_id, self.eval_func, stats=stats)
            stats.elapsed = time.perf_counter() - start
        stats.completed_depth = self.depth
        self.last_stats = stats
        return move