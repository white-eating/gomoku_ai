"""
五子棋 / 井字棋 Pygame 图形界面（第三周）。
布局：左侧棋盘区 + 右侧控制面板，固定窗口 840×620。
功能：人机对弈 / AI 自对弈 / 模式切换 / 悔棋 / 重新开始 / 胜负弹窗。
"""
import sys
import pygame

from board import GomokuBoard, TicTacToeBoard
from game import Game
from minimax import MinimaxPlayer, evaluate_gomoku, evaluate_tic_tac_toe
from player import HumanPlayer, Player

# ==================== 窗口常量 ====================
WINDOW_W, WINDOW_H = 840, 620

BOARD_X, BOARD_Y = 15, 15
BOARD_W, BOARD_H = 560, 560

PANEL_X = BOARD_X + BOARD_W + 15       # 590
PANEL_Y, PANEL_W, PANEL_H = 15, 225, 560

# ==================== 配色 ====================
C_BG_DARK      = (38, 30, 22)
C_BOARD_BG     = (220, 180, 140)
C_GRID_LINE    = (80, 40, 0)
C_BLACK        = (30, 30, 30)
C_WHITE        = (235, 235, 235)
C_HIGHLIGHT    = (255, 255, 255)
C_LAST_MARK    = (220, 50, 50)
C_LABEL        = (120, 80, 40)
C_PANEL_BG     = (50, 42, 32)
C_PANEL_BORDER = (90, 75, 55)
C_TEXT         = (230, 215, 185)
C_TEXT_DIM     = (160, 140, 110)
C_ACCENT       = (200, 160, 80)
C_GREEN        = (130, 200, 100)
C_RED          = (230, 90, 80)
C_BTN          = (70, 55, 38)
C_BTN_HOVER    = (110, 85, 55)
C_BTN_BORDER   = (140, 115, 80)
C_BTN_TEXT     = (235, 225, 200)
C_OVERLAY      = (0, 0, 0, 155)


class _DummyHuman(Player):
    """占位人类玩家（GUI 不通过 Player.get_move 落子）。"""
    def get_move(self, board):
        raise NotImplementedError


class GomokuGUI:
    """五子棋/井字棋人机对弈 + AI 自对弈 图形界面。"""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption("下棋 AI — 五子棋 / 井字棋")
        self.clock = pygame.time.Clock()
        self._init_fonts()
        self.use_tt = True  # 置换表缓存，默认开启
        self._new_game("gomoku")
        self.running = True

    # ========== 字体 ==========

    def _init_fonts(self):
        path = self._find_font()
        if path:
            self.font_11 = pygame.font.Font(path, 16)
            self.font_13 = pygame.font.Font(path, 20)
            self.font_15 = pygame.font.Font(path, 24)
            self.font_18 = pygame.font.Font(path, 30)
            self.font_24 = pygame.font.Font(path, 40)
            self.font_36 = pygame.font.Font(path, 56)
        else:
            self.font_11 = pygame.font.Font(None, 16)
            self.font_13 = pygame.font.Font(None, 20)
            self.font_15 = pygame.font.Font(None, 24)
            self.font_18 = pygame.font.Font(None, 30)
            self.font_24 = pygame.font.Font(None, 40)
            self.font_36 = pygame.font.Font(None, 56)

    @staticmethod
    def _find_font() -> str:
        import os as _os
        for p in ["C:/Windows/Fonts/msyh.ttc",
                   "C:/Windows/Fonts/simhei.ttf",
                   "C:/Windows/Fonts/simsun.ttc"]:
            if _os.path.isfile(p):
                return p
        return ""

    # ========== 游戏初始化 ==========

    def _new_game(self, mode: str = None):
        """创建新对局。mode = 'gomoku' | 'ttt'。"""
        if mode is not None:
            self.mode = mode

        if self.mode == "ttt":
            self.size = 3
            self.cell_w = BOARD_W / 3     # 每个格子的宽 (~187px)
            self.cell_h = BOARD_H / 3     # 每个格子的高 (~187px)
            self.board = TicTacToeBoard()
            self.ai_human = MinimaxPlayer(
                player_id=2, depth=9, use_alpha_beta=True,
                eval_func=evaluate_tic_tac_toe,
                use_transposition_table=self.use_tt,
            )
            mode_label = "井字棋  3×3"
        else:
            self.size = 15
            self.cell_size = 38
            self.grid_px = self.cell_size * (self.size - 1)  # 532
            self.grid_offset = (BOARD_W - self.grid_px) // 2  # 14
            self.board = GomokuBoard(size=15)
            self.ai_human = MinimaxPlayer(
                player_id=2, depth=6, use_alpha_beta=True,
                eval_func=evaluate_gomoku, iterative=True,
                time_limit=2.0, max_moves=30,
                use_transposition_table=self.use_tt,
            )
            mode_label = "五子棋  15×15"

        self.mode_label = mode_label
        self.game = Game(self.board, _DummyHuman(), self.ai_human)
        self.hover_cell = None
        self.ai_thinking = False
        self.last_ai_stats = None
        self.self_play = False
        self.self_play_paused = False
        self._popup_btn = None

    # ========== AI 自对弈 ==========

    def _start_self_play(self):
        """启动 AI vs AI 自动对弈。"""
        self._new_game(self.mode)
        self.self_play = True
        self.self_play_paused = False
        # 为双方各创建一个 AI
        if self.mode == "ttt":
            self.ai_black = MinimaxPlayer(
                player_id=1, depth=9, use_alpha_beta=True,
                eval_func=evaluate_tic_tac_toe,
                use_transposition_table=self.use_tt,
            )
            self.ai_white = MinimaxPlayer(
                player_id=2, depth=9, use_alpha_beta=True,
                eval_func=evaluate_tic_tac_toe,
                use_transposition_table=self.use_tt,
            )
        else:
            self.ai_black = MinimaxPlayer(
                player_id=1, depth=6, use_alpha_beta=True,
                eval_func=evaluate_gomoku, iterative=True,
                time_limit=2.0, max_moves=30,
                use_transposition_table=self.use_tt,
            )
            self.ai_white = MinimaxPlayer(
                player_id=2, depth=6, use_alpha_beta=True,
                eval_func=evaluate_gomoku, iterative=True,
                time_limit=2.0, max_moves=30,
                use_transposition_table=self.use_tt,
            )
        self.game = Game(self.board, self.ai_black, self.ai_white)
        self.last_ai_stats = None

    # ========== 坐标换算 ==========

    def _grid_origin(self):
        return BOARD_X + self.grid_offset, BOARD_Y + self.grid_offset

    def _cell_to_pixel(self, r: int, c: int):
        ox, oy = self._grid_origin()
        return ox + c * self.cell_size, oy + r * self.cell_size

    def _pixel_to_cell(self, px: int, py: int):
        if self.mode == "ttt":
            # 井字棋：检测点击在哪个格子
            c = int((px - BOARD_X) / self.cell_w)
            r = int((py - BOARD_Y) / self.cell_h)
            if 0 <= r < 3 and 0 <= c < 3:
                return r, c
            return None
        ox, oy = self._grid_origin()
        c = round((px - ox) / self.cell_size)
        r = round((py - oy) / self.cell_size)
        if 0 <= r < self.size and 0 <= c < self.size:
            cx, cy = self._cell_to_pixel(r, c)
            if abs(px - cx) <= self.cell_size // 2 and abs(py - cy) <= self.cell_size // 2:
                return r, c
        return None

    def _in_board(self, pos):
        if self.mode == "ttt":
            return (BOARD_X <= pos[0] <= BOARD_X + BOARD_W and
                    BOARD_Y <= pos[1] <= BOARD_Y + BOARD_H)
        ox, oy = self._grid_origin()
        return (ox - self.cell_size//2 <= pos[0] <= ox + self.grid_px + self.cell_size//2 and
                oy - self.cell_size//2 <= pos[1] <= oy + self.grid_px + self.cell_size//2)

    # ================================================================
    #  绘制 — 棋盘
    # ================================================================

    def _draw_board(self):
        bx, by = BOARD_X, BOARD_Y

        # 井字棋白底，五子棋木色底
        bg = (245, 245, 240) if self.mode == "ttt" else C_BOARD_BG
        grid_c = (50, 50, 50) if self.mode == "ttt" else C_GRID_LINE

        pygame.draw.rect(self.screen, bg, (bx, by, BOARD_W, BOARD_H), border_radius=4)
        pygame.draw.rect(self.screen, grid_c, (bx, by, BOARD_W, BOARD_H), width=1, border_radius=4)

        ox, oy = self._grid_origin()

        # ---- 网格线 ----
        grid_c = (50, 50, 50) if self.mode == "ttt" else C_GRID_LINE
        if self.mode == "ttt":
            # 井字棋：两条横线 + 两条竖线 = # 字
            for i in range(1, 3):
                y = BOARD_Y + i * self.cell_h
                pygame.draw.line(self.screen, grid_c, (BOARD_X, y),
                                 (BOARD_X + BOARD_W, y), 4)
                x = BOARD_X + i * self.cell_w
                pygame.draw.line(self.screen, grid_c, (x, BOARD_Y),
                                 (x, BOARD_Y + BOARD_H), 4)
        else:
            for i in range(self.size):
                sx, sy = ox, oy + i * self.cell_size
                ex, ey = ox + self.grid_px, oy + i * self.cell_size
                pygame.draw.line(self.screen, grid_c, (sx, sy), (ex, ey), 1)
                sx, sy = ox + i * self.cell_size, oy
                ex, ey = ox + i * self.cell_size, oy + self.grid_px
                pygame.draw.line(self.screen, grid_c, (sx, sy), (ex, ey), 1)

        # ---- 星位 (仅五子棋) ----
        if self.mode == "gomoku":
            for r, c in [(3,3),(3,7),(3,11),(7,3),(7,7),(7,11),(11,3),(11,7),(11,11)]:
                cx, cy = self._cell_to_pixel(r, c)
                pygame.draw.circle(self.screen, C_GRID_LINE, (cx, cy), 4)

        # ---- 坐标标签 (仅五子棋) ----
        if self.mode == "gomoku":
            cx0, cy0 = self._cell_to_pixel(0, 0)
            lb = self.font_11.render("0", True, C_LABEL)
            self.screen.blit(lb, (cx0 - lb.get_width() - 4, cy0 - lb.get_height() - 2))
            for i in range(1, 15):
                cx, _ = self._cell_to_pixel(0, i)
                lb = self.font_11.render(str(i), True, C_LABEL)
                self.screen.blit(lb, (cx - lb.get_width()//2, by + 4))
                _, cy = self._cell_to_pixel(i, 0)
                lb = self.font_11.render(str(i), True, C_LABEL)
                self.screen.blit(lb, (bx + 4, cy - lb.get_height()//2))

        # ---- 棋子 ----
        b = self.board.board
        for r in range(self.size):
            for c in range(self.size):
                piece = int(b[r, c])
                if piece == 0:
                    continue
                if self.mode == "ttt":
                    self._draw_ttt_piece(r, c, piece)
                else:
                    cx, cy = self._cell_to_pixel(r, c)
                    self._draw_gomoku_piece(cx, cy, piece)

        # ---- 最后落子标记 ----
        if self.board.last_move is not None:
            r, c = self.board.last_move
            if self.mode == "ttt":
                cx = BOARD_X + c * self.cell_w + self.cell_w / 2
                cy = BOARD_Y + r * self.cell_h + self.cell_h / 2
            else:
                cx, cy = self._cell_to_pixel(r, c)
            pygame.draw.circle(self.screen, C_LAST_MARK, (int(cx), int(cy)), 6)

    def _draw_gomoku_piece(self, cx: int, cy: int, piece: int):
        radius = self.cell_size // 2 - 2
        base = C_BLACK if piece == 1 else C_WHITE
        pygame.draw.circle(self.screen, base, (cx, cy), radius)
        hl_r = max(radius // 3, 3)
        hl_c = (90, 90, 90) if piece == 1 else C_HIGHLIGHT
        pygame.draw.circle(self.screen, hl_c,
                           (cx - radius//3, cy - radius//3), hl_r)

    def _draw_ttt_piece(self, r: int, c: int, piece: int):
        """井字棋棋子画在格子中心：X 蓝色，O 红色。"""
        cx = BOARD_X + c * self.cell_w + self.cell_w / 2
        cy = BOARD_Y + r * self.cell_h + self.cell_h / 2
        radius = min(self.cell_w, self.cell_h) // 2 - 20
        if piece == 1:
            color = (65, 130, 220)
            pygame.draw.line(self.screen, color,
                             (cx - radius, cy - radius), (cx + radius, cy + radius), 6)
            pygame.draw.line(self.screen, color,
                             (cx + radius, cy - radius), (cx - radius, cy + radius), 6)
        else:
            color = (220, 70, 100)
            pygame.draw.circle(self.screen, color, (int(cx), int(cy)), radius, width=6)

    def _draw_hover(self):
        if self.hover_cell is None or self.ai_thinking or self.self_play:
            return
        if self.board.is_game_over():
            return
        r, c = self.hover_cell
        if int(self.board.board[r, c]) != 0:
            return

        if self.mode == "ttt":
            cx = BOARD_X + c * self.cell_w + self.cell_w / 2
            cy = BOARD_Y + r * self.cell_h + self.cell_h / 2
            radius = min(self.cell_w, self.cell_h) // 2 - 22
            d = int(radius * 2)
            surf = pygame.Surface((d + 12, d + 12), pygame.SRCALPHA)
            cp = self.board.current_player
            color = (65, 130, 220) if cp == 1 else (220, 70, 100)
            if cp == 1:
                pygame.draw.line(surf, (*color, 70), (6, 6), (d + 6, d + 6), 4)
                pygame.draw.line(surf, (*color, 70), (d + 6, 6), (6, d + 6), 4)
            else:
                pygame.draw.circle(surf, (*color, 70), (d // 2 + 6, d // 2 + 6), radius, width=4)
            self.screen.blit(surf, (cx - radius - 6, cy - radius - 6))
        else:
            cx, cy = self._cell_to_pixel(r, c)
            radius = self.cell_size // 2 - 2
            d = radius * 2
            surf = pygame.Surface((d, d), pygame.SRCALPHA)
            base = C_BLACK if self.board.current_player == 1 else C_WHITE
            pygame.draw.circle(surf, (*base, 90), (radius, radius), radius)
            self.screen.blit(surf, (cx - radius, cy - radius))

    # ================================================================
    #  绘制 — 右侧面板
    # ================================================================

    def _draw_panel(self):
        px, py, pw, ph = PANEL_X, PANEL_Y, PANEL_W, PANEL_H
        pygame.draw.rect(self.screen, C_PANEL_BG, (px, py, pw, ph), border_radius=8)
        pygame.draw.rect(self.screen, C_PANEL_BORDER, (px, py, pw, ph), width=1, border_radius=8)

        cx = px + 15
        cw = pw - 30
        y = py + 16

        # ---- 标题 ----
        title = "五子棋" if self.mode == "gomoku" else "井字棋"
        t = self.font_15.render(title, True, C_ACCENT)
        self.screen.blit(t, (cx + (cw - t.get_width())//2, y))
        y += t.get_height() + 10
        self._hline(cx, y, cw)
        y += 8

        # ---- 模式 ----
        t = self.font_13.render(f"模式：{self.mode_label}", True, C_TEXT)
        self.screen.blit(t, (cx, y))
        y += t.get_height() + 8

        # ---- 玩家 ----
        if self.mode == "ttt":
            p1_name, p2_name = "X (你)", "O (AI)"
        else:
            p1_name, p2_name = "黑棋 (你)", "白棋 (AI)"

        if self.self_play:
            show = f"{p1_name.split()[0]} AI vs {p2_name.split()[0]} AI"
            dot_color = C_TEXT_DIM
        elif self.board.is_game_over():
            show, dot_color = "对局结束", C_TEXT_DIM
        elif self.ai_thinking:
            show = f"{p2_name} 思考中..."
            dot_color = C_ACCENT
        else:
            show = f"你的回合（{p1_name.split()[0]}）"
            dot_color = C_GREEN
        if not self.self_play:
            pygame.draw.circle(self.screen, dot_color, (cx + 5, y + 6), 7)
            pygame.draw.circle(self.screen, C_PANEL_BORDER, (cx + 5, y + 6), 7, width=1)
            indent = 18
        else:
            indent = 0
        t = self.font_13.render(show, True, C_TEXT)
        self.screen.blit(t, (cx + indent, y))
        y += t.get_height() + 8

        # ---- 状态 ----
        w = self.board.get_winner()
        if self.mode == "ttt":
            win_text = {1: "X 胜！", 2: "O 胜！"}
        else:
            win_text = {1: "黑棋胜！", 2: "白棋胜！"}

        if w == 1:
            status, s_color = win_text[1], C_GREEN
        elif w == 2:
            status, s_color = win_text[2], C_RED
        elif self.board.is_game_over():
            status, s_color = "平局", C_TEXT_DIM
        elif self.self_play and self.self_play_paused:
            status, s_color = "已暂停", C_ACCENT
        elif self.self_play:
            status, s_color = "自动对弈中...", C_ACCENT
        elif self.ai_thinking:
            status, s_color = "AI 思考中...", C_ACCENT
        else:
            status, s_color = "进行中", C_GREEN
        st = self.font_13.render("状态：", True, C_TEXT)
        self.screen.blit(st, (cx, y))
        sv = self.font_13.render(status, True, s_color)
        self.screen.blit(sv, (cx + st.get_width(), y))
        y += st.get_height() + 12
        self._hline(cx, y, cw)
        y += 8

        # ---- AI 统计 ----
        t = self.font_13.render("AI 搜索统计", True, C_TEXT_DIM)
        self.screen.blit(t, (cx, y))
        y += t.get_height() + 4
        if self.last_ai_stats is not None:
            s = self.last_ai_stats
            rows = [
                f"完成深度：{s.completed_depth}",
                f"搜 索 量：{s.nodes:,}",
                f"耗时：{s.elapsed:.1f}s",
            ]
            if self.use_tt:
                rate_str = f"{s.tt_hit_rate:.1%}" if s.tt_lookups > 0 else "—"
                rows.append(f"命中率：{rate_str} ({s.tt_hits}/{s.tt_lookups})")
        else:
            rows = ["完成深度：—", "搜 索 量：—", "耗时：—"]
            if self.use_tt:
                rows.append("命中率：—")
        for row in rows:
            t = self.font_11.render(row, True, C_TEXT_DIM)
            self.screen.blit(t, (cx + 4, y))
            y += t.get_height() + 3
        y += 8
        self._hline(cx, y, cw)
        y += 10

        # ---- 按钮 ----
        self._btn_rects = []
        tt_label = "置换表: ✓ 开" if self.use_tt else "置换表: ✗ 关"
        if self.self_play:
            btns = [tt_label, "继续 / 暂停", "停  止", "退  出 (Q)"]
        else:
            btns = [tt_label, "切换模式", "悔  棋 (U)", "重新开始 (N)", "AI 自对弈", "退  出 (Q)"]

        for label in btns:
            bw, bh = cw, 32
            rect = pygame.Rect(cx, y, bw, bh)
            self._btn_rects.append((rect, label))
            hover = rect.collidepoint(pygame.mouse.get_pos())
            bg = C_BTN_HOVER if hover else C_BTN
            pygame.draw.rect(self.screen, bg, rect, border_radius=5)
            pygame.draw.rect(self.screen, C_BTN_BORDER, rect, width=1, border_radius=5)
            txt = label.replace(" (U)", "").replace(" (N)", "").replace(" (Q)", "")
            t = self.font_13.render(txt, True, C_BTN_TEXT)
            self.screen.blit(t, (rect.centerx - t.get_width()//2,
                                 rect.centery - t.get_height()//2))
            y += bh + 6

    def _hline(self, x: int, y: int, w: int):
        pygame.draw.line(self.screen, C_PANEL_BORDER, (x, y), (x + w, y), 1)

    # ================================================================
    #  弹窗
    # ================================================================

    def _draw_popup(self, title: str, subtitle: str):
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill(C_OVERLAY)
        self.screen.blit(overlay, (0, 0))

        pw, ph = 300, 180
        px = (WINDOW_W - pw) // 2
        py = (WINDOW_H - ph) // 2
        pygame.draw.rect(self.screen, (48, 38, 28), (px, py, pw, ph), border_radius=12)
        pygame.draw.rect(self.screen, (180, 150, 100), (px, py, pw, ph), width=2, border_radius=12)

        t1 = self.font_18.render(title, True, C_TEXT)
        self.screen.blit(t1, (px + (pw - t1.get_width())//2, py + 28))
        t2 = self.font_13.render(subtitle, True, C_TEXT_DIM)
        self.screen.blit(t2, (px + (pw - t2.get_width())//2, py + 70))

        bw, bh = 120, 36
        bx = px + (pw - bw)//2
        by = py + ph - bh - 20
        btn = pygame.Rect(bx, by, bw, bh)
        hover = btn.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(self.screen, C_BTN_HOVER if hover else C_BTN,
                         btn, border_radius=6)
        pygame.draw.rect(self.screen, C_BTN_BORDER, btn, width=1, border_radius=6)
        tb = self.font_13.render("再来一局", True, C_BTN_TEXT)
        self.screen.blit(tb, (btn.centerx - tb.get_width()//2,
                              btn.centery - tb.get_height()//2))
        self._popup_btn = btn

    # ================================================================
    #  事件处理
    # ================================================================

    def _handle_click(self, pos):
        """人类落子。"""
        if self.self_play or self.ai_thinking or self.board.is_game_over():
            return
        if not self._in_board(pos):
            return
        cell = self._pixel_to_cell(*pos)
        if cell is None or cell not in self.board.get_legal_moves():
            return
        self.game.do_move(cell)
        if self.board.is_game_over():
            return
        self.ai_thinking = True

    def _do_ai_move(self):
        self._draw_frame()
        pygame.display.flip()
        try:
            cp = self.board.current_player
            if self.self_play:
                ai = self.ai_black if cp == 1 else self.ai_white
                move = ai.get_move(self.board)
                self.game.do_move(move)
                self.last_ai_stats = ai.last_stats
                # 视觉延时
                pygame.time.wait(400)
            else:
                move = self.ai_human.get_move(self.board)
                self.game.do_move(move)
                self.last_ai_stats = self.ai_human.last_stats
        finally:
            self.ai_thinking = False
            # 清除 AI 思考期间在棋盘上的误触点击，保留按钮/键盘事件
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if not self._on_button(event.pos) and self._in_board(event.pos):
                        continue  # 棋盘误触，丢弃
                pygame.event.post(event)  # 其他事件放回队列

    def _handle_undo(self):
        if self.self_play or self.ai_thinking or self.board.is_game_over():
            return
        if self.game.undo(2):
            self.board = self.game.board
            self.last_ai_stats = None

    def _handle_new_game(self):
        self._new_game(self.mode)

    def _toggle_mode(self):
        """切换井字棋 ↔ 五子棋。"""
        new_mode = "ttt" if self.mode == "gomoku" else "gomoku"
        self._new_game(new_mode)

    def _on_button(self, pos):
        for rect, label in self._btn_rects:
            if rect.collidepoint(pos):
                if "置换表" in label:
                    self.use_tt = not self.use_tt
                    self._handle_new_game()
                elif "切换模式" in label:
                    self._toggle_mode()
                elif "悔" in label:
                    self._handle_undo()
                elif "重新开始" in label:
                    self._handle_new_game()
                elif "AI 自对弈" in label:
                    self._start_self_play()
                elif "继续" in label:
                    self.self_play_paused = not self.self_play_paused
                elif "停止" in label or "停" in label:
                    self._new_game(self.mode)  # 回到人机模式
                elif "退" in label:
                    self.running = False
                return True
        return False

    def _on_popup(self, pos):
        if self._popup_btn and self._popup_btn.collidepoint(pos):
            self._handle_new_game()
            return True
        return False

    def _on_key(self, key):
        if key == pygame.K_u and not self.self_play:
            self._handle_undo()
        elif key == pygame.K_n:
            self._handle_new_game()
        elif key == pygame.K_m:
            self._toggle_mode()
        elif key == pygame.K_s:
            self._start_self_play()
        elif key == pygame.K_SPACE and self.self_play:
            self.self_play_paused = not self.self_play_paused
        elif key == pygame.K_q:
            self.running = False

    # ================================================================
    #  主循环
    # ================================================================

    def _draw_frame(self):
        self.screen.fill(C_BG_DARK)
        self._draw_board()
        self._draw_hover()
        self._draw_panel()
        if self.board.is_game_over():
            w = self.board.get_winner()
            is_gomoku = self.mode == "gomoku"
            if w == 1:
                if self.self_play:
                    title = "黑棋 AI 胜！" if is_gomoku else "X AI 胜！"
                else:
                    title = "你赢了！"
                sub = ("黑棋" if is_gomoku else "X") + ("五子连珠" if is_gomoku else " 三子连线")
            elif w == 2:
                if self.self_play:
                    title = "白棋 AI 胜！" if is_gomoku else "O AI 胜！"
                else:
                    title = "AI 获胜"
                sub = ("白棋" if is_gomoku else "O") + ("五子连珠" if is_gomoku else " 三子连线")
            else:
                title = "平局"
                sub = "棋盘已满"
            self._draw_popup(title, sub)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if self.board.is_game_over():
                        self._on_popup(pos)
                    elif not self._on_button(pos):
                        self._handle_click(pos)
                elif event.type == pygame.MOUSEMOTION:
                    self.hover_cell = self._pixel_to_cell(*event.pos)
                elif event.type == pygame.KEYDOWN:
                    self._on_key(event.key)

            # AI 走子（人机模式 或 自动对弈模式）
            if self.ai_thinking:
                self._do_ai_move()
            elif self.self_play and not self.self_play_paused and not self.board.is_game_over():
                # 自动对弈：触发当前玩家 AI
                self.ai_thinking = True

            self._draw_frame()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    GomokuGUI().run()
