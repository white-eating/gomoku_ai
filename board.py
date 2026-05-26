from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

class Board(ABC):
    @abstractmethod
    def get_legal_moves(self) -> List[Tuple[int, int]]:
        """返回当前玩家所有可落子的坐标列表"""
        pass

    @abstractmethod
    def make_move(self, move: Tuple[int, int]) -> None:
        """在棋盘上落子，并自动切换玩家"""
        pass

    @abstractmethod
    def is_game_over(self) -> bool:
        """对局是否结束"""
        pass

    @abstractmethod
    def get_winner(self) -> Optional[int]:
        """返回胜利方 (1 或 2)，平局返回 0，未结束返回 None"""
        pass

    @abstractmethod
    def print_board(self) -> None:
        """在控制台打印当前棋盘"""
        pass

    @property
    @abstractmethod
    def current_player(self) -> int:
        """当前轮到的玩家 (1 或 2)"""
        pass

    @abstractmethod
    def copy(self) -> 'Board':
        """深拷贝当前棋盘（为后续搜索树预留）"""
        pass
