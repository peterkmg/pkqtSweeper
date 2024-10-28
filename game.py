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


# rgb
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


class GameState:
  __slots__ = ('__mode', '__rows', '__cols', '__mines', '__matrix')

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
  def matrix(self) -> list[list[int]]:
    return self.__matrix

  @property
  def mode(self) -> GameMode:
    return self.__mode

  @mode.setter
  def mode(self, mode: GameMode) -> None:
    self.__mode = mode

  def create_state(self) -> None:
    if self.__mode is None:
      raise ValueError('Game mode is not set')

    (self.__mines, self.__rows, self.__cols) = self.__mode.value

    mine_list = random.sample(range(self.__rows * self.__cols), self.__mines)
    mine_list.sort()
    self.__matrix = [
      [-1 if (i * self.__cols + j) in mine_list else 0 for j in range(self.__cols)] for i in range(self.__rows)
    ]

    for row in range(self.__rows):
      for col in range(self.__cols):
        if self.__matrix[row][col] == -1:
          for y in range(max(0, row - 1), min(self.__rows, row + 2)):
            for x in range(max(0, col - 1), min(self.__cols, col + 2)):
              if self.__matrix[y][x] != -1:
                self.__matrix[y][x] += 1
