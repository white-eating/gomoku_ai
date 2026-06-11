# Gomoku AI / TicTacToe AI

本项目用于《人工智能基础》棋类 AI 大作业。当前代码已完成第一周井字棋框架，并补充第二周核心任务：Alpha-Beta 剪枝、迭代加深搜索、15×15 五子棋棋盘与五子连珠胜负判断。

## 已实现功能

### 第一周：井字棋基础

- `Board` 抽象基类。
- `TicTacToeBoard`：3×3 井字棋棋盘。
- `Game` 控制器：轮流落子、历史栈、悔棋。
- 无剪枝 `minimax`。
- 命令行对弈框架。

### 第二周：五子棋核心算法

- `alpha_beta`：在 Minimax 中加入 Alpha-Beta 剪枝。
- `compare_minimax_and_alpha_beta`：验证剪枝前后在同一局面、同一深度下评分和最佳走法一致，并输出节点数和剪枝次数。
- `iterative_deepening_search`：迭代加深搜索，默认时间阈值可设为 2 秒，超时返回上一个完整深度的最佳结果。
- `GomokuBoard`：15×15 五子棋棋盘，继承 `Board`。
- 五子棋胜负判断：从最后落子出发沿 8 个方向扫描，检测五子或以上连珠。
- `evaluate_gomoku`：第一版五元组评分评估函数，用于搜索叶子节点估值。
- 五子棋候选走法生成与预排序：优先搜索已有棋子附近位置，提高 Alpha-Beta 剪枝效率。

## 运行测试

```bash
pytest -q
```

## 第二周验证脚本

```bash
python week2_demo.py
```

输出内容包括：

1. 无剪枝 Minimax 与 Alpha-Beta 的一致性验证。
2. Alpha-Beta 的搜索节点数与剪枝次数。
3. 五子棋迭代加深搜索在 2 秒阈值内完成的最大深度。
4. 15×15 五子棋五子连珠判断示例。

## 代码示例

```python
from board import GomokuBoard
from minimax import MinimaxPlayer, evaluate_gomoku

board = GomokuBoard()
ai = MinimaxPlayer(
    player_id=1,
    depth=6,
    eval_func=evaluate_gomoku,
    use_alpha_beta=True,
    iterative=True,
    time_limit=2.0,
)
move = ai.get_move(board)
print(move)
```

### 第三周：置换表与实验测量

- `ZobristHasher`：为每个棋盘位置和棋子类型生成 64 位随机数，计算局面 Zobrist 哈希。
- `TranspositionTable`：使用字典缓存搜索过的局面，条目包含 `depth`、`value`、`flag`、`best_move`。
- `alpha_beta(..., transposition_table=tt)`：Alpha-Beta 搜索已集成置换表，支持 EXACT / LOWER / UPPER 三类缓存边界。
- `SearchStats`：新增 `tt_lookups`、`tt_hits`、`tt_stores` 和 `tt_hit_rate`，用于统计命中率。
- `compare_transposition_table_speed`：对比普通 Alpha-Beta 与 Alpha-Beta + 置换表的节点数、耗时、命中率和加速比。
- `MinimaxPlayer`：新增 `use_transposition_table` 参数，默认启用。

## 第三周验证脚本

```bash
python week3_demo.py
```

输出内容包括：

1. 普通 Alpha-Beta 与 Alpha-Beta + 置换表的结果一致性。
2. 搜索节点数、剪枝次数、运行时间。
3. 置换表查询次数、命中次数、命中率、缓存条目数量。
4. 2 秒迭代加深搜索中置换表统计信息。
