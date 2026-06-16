# Gomoku AI / TicTacToe AI

本项目用于《人工智能基础》棋类 AI 大作业。代码实现了从井字棋到五子棋的完整博弈系统，包含 Minimax 搜索、Alpha-Beta 剪枝、迭代加深、置换表、MCTS 等多种算法，并提供 CLI 和 GUI 双模式交互界面。

---

## 已实现功能

### 第一周：井字棋基础

- `Board` 抽象基类。
- `TicTacToeBoard`：3×3 井字棋棋盘。
- `Game` 控制器：轮流落子、历史栈、悔棋。
- 无剪枝 `minimax` 搜索。
- 命令行对弈框架。

### 第二周：五子棋核心算法

- `alpha_beta`：在 Minimax 中加入 Alpha-Beta 剪枝。
- `compare_minimax_and_alpha_beta`：验证剪枝前后在同一局面、同一深度下评分和最佳走法一致，并输出节点数和剪枝次数。
- `iterative_deepening_search`：迭代加深搜索，默认时间阈值 2 秒，超时返回上一个完整深度的最佳结果。
- `GomokuBoard`：15×15 五子棋棋盘，继承 `Board`。
- 五子棋胜负判断：从最后落子出发沿 8 个方向扫描，检测五子或以上连珠。
- `evaluate_gomoku`：基于五元组的启发式评估函数，用于搜索叶子节点估值。
- 候选走法生成与预排序：优先搜索已有棋子附近位置，提高 Alpha-Beta 剪枝效率。

### 第三周：置换表与实验测量

- `ZobristHasher`：为每个棋盘位置和棋子类型生成 64 位随机数，计算局面 Zobrist 哈希。
- `TranspositionTable`：使用字典缓存搜索过的局面，条目包含 `depth`、`value`、`flag`、`best_move`。
- `alpha_beta(..., transposition_table=tt)`：Alpha-Beta 搜索集成置换表，支持 EXACT / LOWER / UPPER 三类缓存边界。
- `SearchStats`：新增 `tt_lookups`、`tt_hits`、`tt_stores` 和 `tt_hit_rate`，用于统计命中率。
- `compare_transposition_table_speed`：对比普通 Alpha-Beta 与 Alpha-Beta + 置换表的节点数、耗时、命中率和加速比。
- `MinimaxPlayer`：新增 `use_transposition_table` 参数，默认启用。
- `mcts_from_scratch.py`：从零实现的蒙特卡洛树搜索（纯随机 Rollout），支持与 Minimax 对比。

### 第四周：实验汇总与展示

- `collect_experiment_data.py`：自动化数据采集脚本，运行井字棋剪枝对比 + 五子棋深度胜率测试。
- `compare_mcts_minimax.py`：MCTS vs Minimax 批量对弈实验（50 局），自动生成胜率柱状图。
- `tournament.py`：AI vs AI 通用对弈框架，支持 Minimax / MCTS / Random 任意组合，批量运行并实时显示比分。
- `plot_experiments.py` / `plot_pruning_bars.py`：实验数据可视化，生成剪枝效果柱状图。
- `Gomoku_pre.pptx`：答辩展示 PPT。
- `AI_report.zip`：最终实验报告（含完整 LaTeX 源码和 PDF）。

---

## 运行测试

```bash
pytest -q
```

## 验证脚本

| 脚本 | 说明 |
|------|------|
| `week2_demo.py` | 第二周验证：剪枝一致性、节点数、迭代加深、五子棋胜负判断 |
| `week3_demo.py` | 第三周验证：置换表命中率、加速比、迭代加深统计 |
| `collect_experiment_data.py` | 采集剪枝对比 + 五子棋深度胜率数据 |
| `compare_mcts_minimax.py` | MCTS vs Minimax 50 局对比实验，生成胜率图 |

```bash
python week2_demo.py
python week3_demo.py
python collect_experiment_data.py
python compare_mcts_minimax.py
```

## 代码示例

```python
from board import GomokuBoard
from minimax import MinimaxPlayer, evaluate_gomoku

board = GomokuBoard()
ai = MinimaxPlayer(
    player_id=1,
    depth=4,
    eval_func=evaluate_gomoku,
    use_alpha_beta=True,
    iterative=True,
    time_limit=2.0,
    use_transposition_table=True,
)
move = ai.get_move(board)
print(move)
```

## AI 自对弈

```bash
# Minimax 深度3 vs 深度4，100局
python tournament.py --num-games 100 --player1 minimax --player2 minimax --depth1 3 --depth2 4

# MCTS vs Minimax
python tournament.py --num-games 50 --player1 mcts --player2 minimax --mcts-sim1 500 --depth2 3

# 查看帮助
python tournament.py --help
```

## 图形界面

```bash
python gui.py
```

支持井字棋 / 五子棋切换、鼠标落子、AI 异步计算、信息面板（深度 / 节点数 / 耗时 / 命中率）、悔棋、重新开始。

## 项目结构

```
gomoku_ai/
├── board.py                 # 棋盘基类及 TicTacToeBoard / GomokuBoard
├── minimax.py               # Minimax, Alpha-Beta, 评估函数, 置换表
├── mcts_from_scratch.py     # MCTS 实现
├── game.py                  # 游戏控制器（悔棋、历史栈）
├── cli.py                   # 命令行交互界面
├── gui.py                   # Pygame 图形界面
├── player.py                # 玩家基类及 HumanPlayer / RandomPlayer
├── tournament.py            # AI 自对弈框架
├── week2_demo.py            # 第二周验证脚本
├── week3_demo.py            # 第三周验证脚本
├── collect_experiment_data.py  # 数据采集脚本
├── compare_mcts_minimax.py  # MCTS vs Minimax 对比实验
├── test/                    # 单元测试
└── requirements.txt         # 依赖列表
```

## 依赖安装

```bash
pip install numpy matplotlib pygame pytest
```