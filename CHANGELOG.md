# 第一周 — 改动记录（陈艾嘉）

## 改动处

- `game.py`：`__init__` 新增 `self.history` 历史栈；`play()` 落子前调用 `do_move()` 保存副本；新增 `do_move(move)` 方法（落子+存历史）和 `undo(steps)` 方法（撤销指定步数）
- `cli.py`：新增 `CLI` 类（`get_human_move` 输入验证+命令识别、`run` 手动编排每一步），支持 `undo`/`new`/`quit` 命令交互
- `main.py`：新增 `run_human_vs_ai()` 函数，`__main__` 默认启动人机对弈（Human vs Random）
- `.gitignore`：新增 `.pytest_cache/` 规则，忽略 pytest 测试缓存目录

## 已实现功能

### For CLI 和悔棋
- 打印棋盘：`board.print_board()` 可以直接调用
- 人类输入：`CLI.get_human_move()` 支持坐标输入和命令输入（undo / new / quit）
- 主循环：`CLI.run()` 手动编排每一步（人类输入 → 落子 → AI 回应 → 判终）
- 悔棋功能：`Game.undo(steps)` 方法，基于内部 history 栈实现
- 命令行：`python cli.py` 直接启动人机对弈，对局结束可再来一局

### 运行方式

进入项目目录后执行以下命令：

```bash
python cli.py
```

或：

```bash
python main.py
```

启动后显示：

```
=== 井字棋 人机对弈 ===
人类: X    AI: O
输入坐标如 '0 1'，或命令 undo / new / quit

  0 1 2
0 . . .
1 . . .
2 . . .

玩家 1 请输入坐标或命令 (undo/new/quit):
```

- `python cli.py` → 人机对弈（Human vs Random），对局结束可再来一局
- `python main.py` → 人机对弈（Human vs Random）
- `run_random_vs_random(n)` → 批量随机对战统计（在 main.py 中）

## 注意点

- **悔棋函数位置**：`Game.undo()` 方法，位于 `game.py` 第 35 行
- **悔棋**：从 history 栈弹出棋盘副本并恢复，一次 `undo(2)` 撤销两步（AI + 人类），恢复到人类回合之前；已弹出的副本直接丢弃，不可"反悔棋"（即撤销后无法再恢复）
- `Game.do_move(move)` 是手动循环（CLI）专用的落子接口，会自动保存历史；`board.make_move(move)` 不会保存历史，直接使用会导致 undo 失效
- `Game.play()` 内部已调用 `do_move()`，自动保存历史，直接用它也能配合 undo
- 每次 undo 后 history 已消耗，连续 undo 会持续回退直到 history 为空

# 第二周 — 改动记录（周佳明）

## 改动处

- 在 `minimax.py` 中加入 `alpha_beta`

- 增加 `compare_minimax_and_alpha_beta`，用于验证剪枝前后结果一致

- 实现 `iterative_deepening_search`，支持 2 秒时间阈值

* 在 `board.py` 中新增 `GomokuBoard(Board)`

- 实现 15×15 五子棋棋盘

- 实现五子棋 8 方向扫描胜负判断

- 补充 `evaluate_gomoku` 五元组基础评估函数

- 新增 `week2_demo.py` 验证脚本

- 新增第二周测试文件，测试结果为：

```bash
passed
```
