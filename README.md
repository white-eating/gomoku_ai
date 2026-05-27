# 现在已经实现的功能
## 1. For Minimax
- 棋盘状态拷贝：`copy()`方法
- 合法落子：`get_legal_moves()`和`make_move()`
- 终局判定：`is_game_over()` 和 `get_winner()` （可直接用于评估函数）
- 当前玩家：`current_player`判定该谁走

## 2. For CLI和悔棋
- 打印棋盘：`board.print_board()`可以直接调用
- 人类输入：可以复用 `HumanPlayer`
- 主循环：可以直接使用`Game` 类（传入 `HumanPlayer` 和 `MinimaxPlayer` 即可）
- 悔棋功能：目前没有 undo 方法（但使用外部栈即可）

# 需要知道的事情
- `Board` 的所有方法签名及行为，尤其是 `copy()` 是深度拷贝，模拟走棋后不会影响原棋盘。
- `make_move` 会自动切换玩家并判定游戏是否结束，无需手动管理回合。
- `get_winner()` 的返回值含义：1（玩家1胜）、2（玩家2胜）、0（平局）、None（未结束）。
- 游戏循环 `Game.play()` 会持续调用当前玩家的 `get_move` 并执行`make_move`，直到结束。只需提供自己的 `Player` 子类即可插入。
