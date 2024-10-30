import random
from enum import Enum
from dataclasses import dataclass


@dataclass(frozen=True)
class Cfg:
  wind_hrz_offset: int = 0
  wind_vrt_offset: int = 25
  menu_grp_height: int = 250
  menu_btn_height: int = 40
  game_btn_height: int = 40
  game_btn_width: int = 100
  tile_txt_flagged: str = '🚩'
  tile_txt_question: str = '❓'
  tile_txt_mine: str = '💥'


class GameMode(Enum):
  BEGINNER = (10, 9, 9)
  INTERMEDIATE = (40, 16, 16)
  EXPERT = (99, 16, 30)


class TileButtonState(Enum):
  DEFAULT = 0
  FLAGGED = 1
  QUESTION = 2

  def next(self) -> 'TileButtonState':
    return {
      TileButtonState.DEFAULT: TileButtonState.FLAGGED,
      TileButtonState.FLAGGED: TileButtonState.QUESTION,
      TileButtonState.QUESTION: TileButtonState.DEFAULT,
    }[self]


class TileEventType(Enum):
  OPENSINGLE = 0
  OPENSQUARE = 1
  MARK = 2


class TileNumberColor(Enum):
  # 1 is blue
  ONE = (0, 0, 255)
  # 2 is green
  TWO = (0, 128, 0)
  # 3 is red
  THREE = (255, 0, 0)
  # 4 is navy
  FOUR = (0, 0, 128)
  # 5 is maroon
  FIVE = (128, 0, 0)
  # 6 is teal
  SIX = (0, 128, 128)
  # 7 is black
  SEVEN = (0, 0, 0)
  # 8 is purple
  EIGHT = (128, 0, 128)

  @staticmethod
  def by_val(val: int) -> 'TileNumberColor':
    return {
      1: TileNumberColor.ONE,
      2: TileNumberColor.TWO,
      3: TileNumberColor.THREE,
      4: TileNumberColor.FOUR,
      5: TileNumberColor.FIVE,
      6: TileNumberColor.SIX,
      7: TileNumberColor.SEVEN,
      8: TileNumberColor.EIGHT,
    }[val]


class Board:
  __slots__ = ('__rows', '__cols', '__mines', '__coords', '__mine_placement')

  @property
  def rows(self) -> int:
    return self.__rows

  @property
  def cols(self) -> int:
    return self.__cols

  @property
  def mines(self) -> int:
    return self.__mines

  @property
  def mode(self) -> GameMode:
    return self.__mode

  @property
  def mine_placement(self) -> list[tuple[int, int]]:
    return self.__mine_placement

  def __init__(self, mode: GameMode) -> None:
    (self.__mines, self.__rows, self.__cols) = mode.value
    self.__coords = {(i, j) for i in range(self.__rows) for j in range(self.__cols)}

  def calc_mine_placement(self, row: int, col: int) -> None:
    neighborhood = self.get_square(row, col)
    safe_coords = list(self.__coords.difference(neighborhood))
    self.__mine_placement = random.sample(safe_coords, self.__mines)

  def in_bounds(self, x: int, y: int) -> bool:
    return 0 <= x < self.__cols and 0 <= y < self.__rows

  def get_neighbors(self, row: int, col: int) -> list[tuple[int, int]]:
    return [
      (i, j)
      for i in range(max(0, row - 1), min(self.__rows, row + 2))
      for j in range(max(0, col - 1), min(self.__cols, col + 2))
      if (i, j) != (row, col)
    ]

  def get_square(self, row: int, col: int) -> list[tuple[int, int]]:
    return [
      (i, j)
      for i in range(max(0, row - 1), min(self.__rows, row + 2))
      for j in range(max(0, col - 1), min(self.__cols, col + 2))
    ]
