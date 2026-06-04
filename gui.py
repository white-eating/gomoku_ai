"""
五子棋 Pygame 图形界面（第二周：仅绘图 + 基础落子，不接 AI）。
第三周再对接 Board / MinimaxPlayer。
"""
import sys
import pygame

# ---- 常量 ----
BOARD_SIZE = 15          # 15×15 棋盘
CELL_SIZE = 50           # 每个格子的像素宽度
MARGIN = 80              # 棋盘距窗口边缘的留白
WINDOW_SIZE = MARGIN * 2 + CELL_SIZE * (BOARD_SIZE - 1)  # 860
STAR_POINTS = {          # 五子棋标准星位（行列索引）
    (3, 3), (3, 7), (3, 11),
    (7, 3), (7, 7), (7, 11),
    (11, 3), (11, 7), (11, 11),
}

# 颜色
COLOR_BG = (220, 180, 140)        # 木色棋盘背景
COLOR_LINE = (80, 40, 0)          # 深棕网格线
COLOR_BLACK = (30, 30, 30)        # 黑子
COLOR_WHITE = (235, 235, 235)     # 白子
COLOR_HIGHLIGHT = (255, 255, 255) # 棋子高光（白色半透明感）
COLOR_LAST_MOVE = (220, 50, 50)   # 最后落子红点标记
COLOR_LABEL = (120, 80, 40)       # 坐标标签


class GomokuGUI:
    """五子棋棋盘窗口（纯绘图 + 鼠标落子，不接 AI）。"""

    def __init__(self, board_size: int = BOARD_SIZE):
        self.size = board_size
        # 用二维列表记录棋子：0=空, 1=黑子, 2=白子
        self.board = [[0] * self.size for _ in range(self.size)]
        self.current_player = 1     # 1=黑(先手), 2=白
        self.last_move = None       # (r, c)，用于画红色标记

        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("五子棋")
        # Font(None) 使用 Pygame 内置默认字体（SysFont 在 2.6.1 + Python 3.13 有 Windows bug）
        self.font = pygame.font.Font(None, 16)
        self.hover_cell = None  # 鼠标悬停的交叉点，用于预览落子

    # ========== 坐标换算 ==========

    def _cell_to_pixel(self, r: int, c: int) -> tuple[int, int]:
        """棋盘交叉点 (r,c) → 屏幕像素坐标。"""
        x = MARGIN + c * CELL_SIZE
        y = MARGIN + r * CELL_SIZE
        return x, y

    def _pixel_to_cell(self, px: int, py: int) -> tuple[int, int] | None:
        """屏幕像素 → 最近的棋盘交叉点。距离超过半格则返回 None。"""
        c = round((px - MARGIN) / CELL_SIZE)
        r = round((py - MARGIN) / CELL_SIZE)
        if 0 <= r < self.size and 0 <= c < self.size:
            # 检查是否离交叉点足够近
            cx, cy = self._cell_to_pixel(r, c)
            if abs(px - cx) <= CELL_SIZE // 3 and abs(py - cy) <= CELL_SIZE // 3:
                return r, c
        return None

    # ========== 绘制 ==========

    def _draw_board(self):
        """画背景 + 网格线 + 星位点 + 坐标标签。"""
        self.screen.fill(COLOR_BG)

        # 网格线
        for i in range(self.size):
            # 横线
            start_x, start_y = self._cell_to_pixel(0, i)
            end_x, end_y = self._cell_to_pixel(self.size - 1, i)
            pygame.draw.line(self.screen, COLOR_LINE, (start_x, start_y), (end_x, end_y), 1)
            # 竖线
            start_x, start_y = self._cell_to_pixel(i, 0)
            end_x, end_y = self._cell_to_pixel(i, self.size - 1)
            pygame.draw.line(self.screen, COLOR_LINE, (start_x, start_y), (end_x, end_y), 1)

        # 星位点
        for r, c in STAR_POINTS:
            cx, cy = self._cell_to_pixel(r, c)
            pygame.draw.circle(self.screen, COLOR_LINE, (cx, cy), 4)

        # 坐标标签（列号在棋盘上方，行号在棋盘左侧）
        for i in range(self.size):
            # 列号
            cx, _ = self._cell_to_pixel(0, i)
            label = self.font.render(str(i), True, COLOR_LABEL)
            self.screen.blit(label, (cx - 4, MARGIN - 24))
            # 行号
            _, cy = self._cell_to_pixel(i, 0)
            label = self.font.render(str(i), True, COLOR_LABEL)
            self.screen.blit(label, (MARGIN - 24, cy - 8))

    def _draw_pieces(self):
        """画所有棋子 + 高光 + 最后落子标记。"""
        for r in range(self.size):
            for c in range(self.size):
                piece = self.board[r][c]
                if piece == 0:
                    continue
                cx, cy = self._cell_to_pixel(r, c)
                radius = CELL_SIZE // 2 - 3

                # 棋子底色
                base_color = COLOR_BLACK if piece == 1 else COLOR_WHITE
                pygame.draw.circle(self.screen, base_color, (cx, cy), radius)

                # 高光（小一点的白圈偏左上，模拟光泽）
                hl_r = radius // 2
                hl_x = cx - radius // 3
                hl_y = cy - radius // 3
                hl_color = (90, 90, 90) if piece == 1 else COLOR_HIGHLIGHT
                pygame.draw.circle(self.screen, hl_color, (hl_x, hl_y), max(hl_r, 3))

        # 最后落子红色三角标记
        if self.last_move is not None:
            r, c = self.last_move
            cx, cy = self._cell_to_pixel(r, c)
            mark_r = 5
            pygame.draw.circle(self.screen, COLOR_LAST_MOVE, (cx, cy), mark_r)

    def _draw_hover(self):
        """在鼠标悬停的空交叉点显示半透明预览棋子。"""
        if self.hover_cell is None:
            return
        r, c = self.hover_cell
        if self.board[r][c] != 0:
            return  # 已有棋子，不显示预览

        cx, cy = self._cell_to_pixel(r, c)
        radius = CELL_SIZE // 2 - 3
        diameter = radius * 2
        # 创建带 alpha 通道的临时 surface 画半透明圆
        hover_surf = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        base_color = COLOR_BLACK if self.current_player == 1 else COLOR_WHITE
        color_with_alpha = (*base_color, 120)  # alpha=120/255 ≈ 半透明
        pygame.draw.circle(hover_surf, color_with_alpha, (radius, radius), radius)
        self.screen.blit(hover_surf, (cx - radius, cy - radius))

    # ========== 主循环 ==========

    def run(self):
        """启动棋盘窗口，鼠标点击落子，点 × 关闭。"""
        clock = pygame.time.Clock()
        running = True
        while running:
            # 追踪鼠标悬停位置
            self.hover_cell = self._pixel_to_cell(*pygame.mouse.get_pos())

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    px, py = event.pos
                    cell = self._pixel_to_cell(px, py)
                    if cell is None:
                        continue
                    r, c = cell
                    if self.board[r][c] != 0:
                        continue  # 已有棋子，忽略
                    # 落子
                    self.board[r][c] = self.current_player
                    self.last_move = (r, c)
                    self.current_player = 3 - self.current_player  # 1↔2 切换

            self._draw_board()
            self._draw_pieces()
            self._draw_hover()
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    gui = GomokuGUI()
    gui.run()
