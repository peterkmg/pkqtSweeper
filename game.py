from enum import Enum
import random


# value represents (mines, rows, columns)
class GameMode(Enum):
  BEGINNER = (10, 9, 9)
  INTERMEDIATE = (40, 16, 16)
  EXPERT = (99, 16, 30)


class GameState:
  mode: GameMode
  rows: int
  cols: int
  mines: int

  mine_list: list[int]
  matrix: list[list[int]]

  def __init__(self, mode: GameMode):
    self.mode = mode
    self.mines = mode.value[0]
    self.rows = mode.value[1]
    self.cols = mode.value[2]

    # get random mine placement
    self.mine_list = random.sample(range(self.rows * self.cols), self.mines)

    # initialize test matrix
    self.matrix = [[-1 if (i + j) in self.mine_list else 0 for j in range(self.cols)] for i in range(self.rows)]

    # calculate mine count for each cell
    # iterate through matrix
    # if mine found increase count for all adjacent cells (considering board limits)
    # unless cell value is -1 (mine)
    for row in range(self.rows):
      for col in range(self.cols):
        if self.matrix[row][col] == -1:
          for y in range(max(0, row - 1), min(self.rows, row + 2)):
            for x in range(max(0, col - 1), min(self.cols, col + 2)):
              if self.matrix[y][x] != -1:
                self.matrix[y][x] += 1
