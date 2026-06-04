from board import TicTacToeBoard
from player import HumanPlayer, RandomPlayer
from game import Game


class CLI:
    """命令行交互界面，管理人类 vs AI 对弈流程。"""

    def __init__(self, game: Game):
        self.game = game

    def get_human_move(self):
        """读取人类输入，返回 ('move', (r,c)) 或 ('cmd', <命令名>)。"""
        while True:
            try:
                raw = input(f"玩家 {self.game.board.current_player} 请输入坐标或命令 (undo/new/quit): ").strip()
            except (EOFError, KeyboardInterrupt):
                return ("cmd", "quit")

            if not raw:
                continue

            # 命令识别
            if raw.lower() == "undo":
                return ("cmd", "undo")
            if raw.lower() == "new":
                return ("cmd", "new")
            if raw.lower() == "quit":
                return ("cmd", "quit")

            # 坐标识别
            parts = raw.split()
            if len(parts) == 2:
                try:
                    r, c = int(parts[0]), int(parts[1])
                    if (r, c) in self.game.board.get_legal_moves():
                        return ("move", (r, c))
                    else:
                        print("该位置不合法或已被占据，请重新输入。")
                        continue
                except ValueError:
                    pass

            print("输入格式错误。请输入坐标如 '0 1'，或命令 undo / new / quit。")

    def run(self):
        """主循环：人类输入 → 落子 → AI 回应 → 重复。"""
        print("=== 井字棋 人机对弈 ===")
        print("人类: X    AI: O")
        print("输入坐标如 '0 1'，或命令 undo / new / quit\n")

        while not self.game.board.is_game_over():
            self.game.board.print_board()

            # 人类回合
            result = self.get_human_move()
            if result[0] == "cmd":
                cmd = result[1]
                if cmd == "undo":
                    if self.game.undo(2):
                        print("已悔棋 (撤销 AI + 人类各一步)。")
                    else:
                        print("无法悔棋：没有历史记录。")
                    continue
                elif cmd == "new":
                    print("\n=== 新游戏 ===\n")
                    return "new"
                elif cmd == "quit":
                    print("退出游戏。")
                    return "quit"
            else:
                move = result[1]
                self.game.do_move(move)

            # 检查人类是否获胜
            if self.game.board.is_game_over():
                break

            # AI 回合
            ai_player = self.game.players[self.game.board.current_player]
            ai_move = ai_player.get_move(self.game.board)
            print(f"AI 选择: {ai_move[0]} {ai_move[1]}")
            self.game.do_move(ai_move)

        self.game.board.print_board()
        winner = self.game.board.get_winner()
        if winner == 0:
            print("平局！")
        else:
            symbol = "X" if winner == 1 else "O"
            name = "人类" if winner == 1 else "AI"
            print(f"玩家 {winner} ({name}, {symbol}) 获胜！")

        return winner


if __name__ == "__main__":
    while True:
        board = TicTacToeBoard()
        from minimax import MinimaxPlayer
        human_player = HumanPlayer()
        ai_player = MinimaxPlayer(player_id=2,depth=9,use_alpha_beta=True)
        game = Game(board, HumanPlayer(),ai_player)
        cli = CLI(game)
        result = cli.run()
        if result == "quit":
            break
        if result == "new":
            continue
        # 正常结束（有人获胜或平局）
        again = input("\n再来一局？(y/n): ").strip().lower()
        if again != "y":
            break
