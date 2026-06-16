# compare_mcts_minimax.py (英文版，无需中文字体)
import time
import matplotlib.pyplot as plt
import numpy as np
from board import GomokuBoard
from minimax import MinimaxPlayer
from mcts_from_scratch import MCTSPlayer

class TrackingMinimaxPlayer(MinimaxPlayer):
    """记录每步搜索节点数的 Minimax 玩家"""
    def __init__(self, player_id: int, **kwargs):
        super().__init__(player_id, **kwargs)
        self.node_counts = []

    def get_move(self, board):
        move = super().get_move(board)
        if self.last_stats:
            self.node_counts.append(self.last_stats.nodes)
        else:
            self.node_counts.append(0)
        return move

    def clear_stats(self):
        self.node_counts = []

def play_one_game(mcts: MCTSPlayer, minimax: TrackingMinimaxPlayer, verbose=False) -> int:
    board = GomokuBoard(size=9)
    players = {1: mcts, 2: minimax}
    mcts.player_id = 1
    minimax.player_id = 2
    minimax.clear_stats()

    while not board.is_game_over():
        cur = players[board.current_player]
        move = cur.get_move(board)
        board.make_move(move)
        if verbose:
            board.print_board()
    return board.get_winner()

def run_experiment(num_games=50, mcts_simulations=500, minimax_depth=3, max_moves=24):
    print(f"Experiment config: MCTS({mcts_simulations} sims) vs Minimax(depth={minimax_depth}, max_moves={max_moves})")
    print(f"Board: 9x9, Games: {num_games}")
    wins_mcts = wins_minimax = draws = 0
    all_node_counts = []

    for i in range(1, num_games + 1):
        start_time = time.time()
        mcts = MCTSPlayer(player_id=1, num_simulations=mcts_simulations)
        minimax = TrackingMinimaxPlayer(player_id=2, depth=minimax_depth,
                                        use_alpha_beta=True, max_moves=max_moves,
                                        use_transposition_table=True)
        winner = play_one_game(mcts, minimax, verbose=False)
        if winner == 1:
            wins_mcts += 1
        elif winner == 2:
            wins_minimax += 1
        else:
            draws += 1

        all_node_counts.append(minimax.node_counts.copy())
        elapsed = time.time() - start_time
        print(f"[{i}/{num_games}] Time {elapsed:.1f}s | Score MCTS:{wins_mcts}  Minimax:{wins_minimax}  Draw:{draws}")

    # Statistics
    total_nodes_per_game = [sum(game) for game in all_node_counts if game]
    avg_nodes_per_game = np.mean(total_nodes_per_game) if total_nodes_per_game else 0
    all_nodes = [node for game in all_node_counts for node in game]
    avg_nodes_per_move = np.mean(all_nodes) if all_nodes else 0

    print("\n========== Results ==========")
    print(f"MCTS wins: {wins_mcts}, Minimax wins: {wins_minimax}, Draws: {draws}")
    print(f"Minimax avg nodes per game: {avg_nodes_per_game:.0f}")
    print(f"Minimax avg nodes per move: {avg_nodes_per_move:.0f}")

    # Plotting (English labels only)
    plt.figure(figsize=(12, 5))

    # Subplot 1: Win rate bar chart
    plt.subplot(1, 2, 1)
    labels = ['MCTS', 'Minimax']
    wins = [wins_mcts, wins_minimax]
    bars = plt.bar(labels, wins, color=['#2ecc71', '#e67e22'])
    plt.title(f'MCTS vs Minimax (9x9, {num_games} games, draws={draws})', fontsize=12)
    plt.ylabel('Number of wins')
    for bar, win in zip(bars, wins):
        plt.text(bar.get_x() + bar.get_width()/2, win + 0.5, str(win), ha='center', va='bottom')

    # Subplot 2: Nodes per game boxplot
    plt.subplot(1, 2, 2)
    if total_nodes_per_game:
        plt.boxplot(total_nodes_per_game, vert=True, patch_artist=True)
        plt.title('Minimax search nodes per game', fontsize=12)
        plt.ylabel('Number of nodes (log scale)')
        plt.yscale('log')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
    else:
        plt.text(0.5, 0.5, "No node data", ha='center', va='center')

    plt.tight_layout()
    plt.savefig('mcts_vs_minimax_50.png', dpi=150)
    plt.show()

if __name__ == "__main__":
    # You can adjust parameters here
    run_experiment(num_games=50, mcts_simulations=500, minimax_depth=3, max_moves=24)