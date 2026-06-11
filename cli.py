import random
from board import TicTacToeBoard, GomokuBoard
from player import HumanPlayer
from game import Game
from minimax import MinimaxPlayer, evaluate_gomoku


class CLI:
    """命令行交互界面，管理各种对战模式的流程。"""

    def __init__(self, game: Game, mode_name: str = "井字棋"):
        self.game = game
        self.mode_name = mode_name

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
        """主循环：处理回合制落子。"""
        print(f"\n=== {self.mode_name} ===")
        
        p1_type = "X (人类)" if isinstance(self.game.players[1], HumanPlayer) else "X (AI)"
        p2_type = "O (人类)" if isinstance(self.game.players[2], HumanPlayer) else "O (AI)"
        print(f"{p1_type}   VS   {p2_type}")
        print("输入坐标如 '0 1'，或命令 undo / new / quit\n")

        is_first_move = True  # 标记是否为开局第一步

        while not self.game.board.is_game_over():
            self.game.board.print_board()
            
            current_player_obj = self.game.players[self.game.board.current_player]

            # 如果是人类玩家，等待输入
            if isinstance(current_player_obj, HumanPlayer):
                result = self.get_human_move()
                if result[0] == "cmd":
                    cmd = result[1]
                    if cmd == "undo":
                        if self.game.undo(2):
                            print("已悔棋 (撤销双方各一步)。")
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
            else:
                # 如果是 AI 玩家，自动落子
                role = "黑方(X)" if self.game.board.current_player == 1 else "白方(O)"
                
                # 判断是否为机机对弈的第一步，如果是则随机落子
                legal_moves = self.game.board.get_legal_moves()
                if is_first_move and not isinstance(self.game.players[1], HumanPlayer) and not isinstance(self.game.players[2], HumanPlayer):
                    move = random.choice(list(legal_moves))
                    print(f"[{role} - {current_player_obj.name}] 开局随机落子: {move[0]} {move[1]}")
                else:
                    ai_move = current_player_obj.get_move(self.game.board)
                    print(f"[{role} - {current_player_obj.name}] 思考后落子: {ai_move[0]} {ai_move[1]}")
                    move = ai_move
                
                self.game.do_move(move)
                is_first_move = False  # 第一步执行完毕，后续正常搜索

            # 检查是否结束
            if self.game.board.is_game_over():
                break

        # 游戏结束，显示最终棋盘
        self.game.board.print_board()
        winner = self.game.board.get_winner()
        if winner == 0:
            print("🎉 平局！")
        else:
            symbol = "X" if winner == 1 else "O"
            name = "人类" if isinstance(self.game.players[winner], HumanPlayer) else self.game.players[winner].name
            print(f"🏆 玩家 {winner} ({name}, {symbol}) 获胜！")

        return "game_over"


def main_menu():
    """主菜单逻辑（首页）。"""
    while True:
        print("\n" + "="*45)
        print("           🏠 下棋AI 综合控制台")
        print("="*45)
        print("1. 井字棋 (3×3)")
        print("2. 五子棋 (15×15)")
        print("3. 退出程序")
        
        choice = input("\n请选择棋种 (1/2/3): ").strip()
        
        if choice == "3":
            return "quit"
        elif choice in ("1", "2"):
            mode_action = select_battle_mode(choice)
            if mode_action == "quit":
                return "quit"
        else:
            print("❌ 输入无效，请输入 1, 2 或 3。")


def select_battle_mode(game_choice):
    """对战模式选择页面。"""
    while True:
        print("\n--- ⚔️ 请选择对战模式 ---")
        print("1. 人机对弈 (人类 vs Minimax AI)")
        print("2. 机机对弈 (Minimax AI vs Minimax AI)")
        print("3. 人人对弈 (人类 vs 人类)")
        print("0. 返回上一级")
        
        mode = input("请选择模式 (0-3): ").strip()
        
        if mode == "0":
            return "back_to_main"
        elif mode == "1":
            # 人机对弈：询问人类想当先手还是后手
            human_color = None
            while human_color not in ("1", "2"):
                human_color = input("请选择您的棋子 (1: 先手 X, 2: 后手 O): ").strip()
                if human_color not in ("1", "2"):
                    print("❌ 输入无效，请输入 1 或 2。")
            human_first = (human_color == "1")
            board, players, mode_name = setup_game_config(game_choice, mode, human_first)
            game_loop(board, players, mode_name)
            return "back_to_main"
        elif mode in ("2", "3"):
            board, players, mode_name = setup_game_config(game_choice, mode)
            game_loop(board, players, mode_name)
            return "back_to_main"
        else:
            print("❌ 输入无效，请输入 0-3 之间的数字。")


def setup_game_config(game_choice, mode, human_first=None):
    """
    根据选择的棋种和对战模式，初始化棋盘和玩家对象。
    参数：
        human_first: 仅在人机模式下使用，True 表示人类先手，False 表示人类后手。
    """
    is_gomoku = (game_choice == "2")
    
    # 1. 初始化棋盘
    board = GomokuBoard() if is_gomoku else TicTacToeBoard()
    game_name = "五子棋" if is_gomoku else "井字棋"
    
    # 2. 根据模式配置玩家
    if mode == "1":  # 人机对弈
        if is_gomoku:
            # 根据 human_first 决定 AI 的 player_id
            ai_player_id = 2 if human_first else 1
            human_player_id = 1 if human_first else 2
            ai = MinimaxPlayer(player_id=ai_player_id, depth=6, use_alpha_beta=True, 
                               eval_func=evaluate_gomoku, iterative=True, time_limit=2.0, max_moves=30)
            ai.name = f"AI ({'后手' if ai_player_id == 2 else '先手'})"
        else:
            ai_player_id = 2 if human_first else 1
            human_player_id = 1 if human_first else 2
            ai = MinimaxPlayer(player_id=ai_player_id, depth=9, use_alpha_beta=True)
            ai.name = f"AI ({'后手' if ai_player_id == 2 else '先手'})"
        
        human = HumanPlayer()
        human.name = f"人类 ({'X' if human_player_id == 1 else 'O'})"
        players = {human_player_id: human, ai_player_id: ai}
        full_mode_name = f"{game_name} - 人机对弈"
        
    elif mode == "2":  # 机机对弈：双 Minimax AI
        if is_gomoku:
            ai1 = MinimaxPlayer(player_id=1, depth=6, use_alpha_beta=True, 
                                eval_func=evaluate_gomoku, iterative=True, time_limit=2.0, max_moves=30)
            ai2 = MinimaxPlayer(player_id=2, depth=6, use_alpha_beta=True, 
                                eval_func=evaluate_gomoku, iterative=True, time_limit=2.0, max_moves=30)
        else:
            ai1 = MinimaxPlayer(player_id=1, depth=9, use_alpha_beta=True)
            ai2 = MinimaxPlayer(player_id=2, depth=9, use_alpha_beta=True)
        
        ai1.name = "AI-1"
        ai2.name = "AI-2"
        players = {1: ai1, 2: ai2}
        full_mode_name = f"{game_name} - 机机对弈 (AI-1 vs AI-2)"
        
    else:  # mode == "3", 人人对弈
        p1 = HumanPlayer()
        p2 = HumanPlayer()
        p1.name = "玩家1 (X)"
        p2.name = "玩家2 (O)"
        players = {1: p1, 2: p2}
        full_mode_name = f"{game_name} - 人人对弈"
        
    return board, players, full_mode_name


def game_loop(board, players, mode_name):
    """游戏对弈循环。"""
    while True:
        game = Game(board.__class__(), players[1], players[2])
        cli = CLI(game, mode_name)
        result = cli.run()

        if result == "quit":
            return
        
        again = input("\n🎮 再来一局？(y/n): ").strip().lower()
        if again != "y":
            print("↩️ 即将返回主菜单...")
            break


# --- 程序入口 ---
if __name__ == "__main__":
    try:
        while True:
            action = main_menu()
            if action == "quit":
                print("\n👋 感谢使用，再见！")
                break
    except KeyboardInterrupt:
        print("\n\n👋 程序被用户中断。")