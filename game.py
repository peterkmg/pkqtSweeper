from enum import Enum
import random


# value represents (mines, rows, columns)
class GameMode(Enum):
  BEGINNER = (10, 9, 9)
  INTERMEDIATE = (40, 16, 16)
  EXPERT = (99, 16, 30)


class TileButtonState(Enum):
  DEFAULT = 0
  FLAGGED = 1
  QUESTION = 2

  def next(self):
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

  def by_val(val: int):
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
  mode: GameMode = None
  rows: int
  cols: int
  mines: int

  matrix: list[list[int]]

  def set_mode(self, mode: GameMode):
    self.mode = mode

  def create_state(self):
    if self.mode is None:
      raise ValueError('Game mode is not set')

    (self.mines, self.rows, self.cols) = self.mode.value

    mine_list = random.sample(range(self.rows * self.cols), self.mines)
    mine_list.sort()
    self.matrix = [[-1 if (i * self.cols + j) in mine_list else 0 for j in range(self.cols)] for i in range(self.rows)]

    for row in range(self.rows):
      for col in range(self.cols):
        if self.matrix[row][col] == -1:
          for y in range(max(0, row - 1), min(self.rows, row + 2)):
            for x in range(max(0, col - 1), min(self.cols, col + 2)):
              if self.matrix[y][x] != -1:
                self.matrix[y][x] += 1
