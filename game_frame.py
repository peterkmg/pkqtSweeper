from typing import Callable
from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtWidgets import (
  QFrame,
  QVBoxLayout,
  QWidget,
  QHBoxLayout,
  QLabel,
  QGridLayout,
  QPushButton,
  QStackedWidget,
  QLCDNumber,
)
from PySide6.QtGui import QMouseEvent

from game import TileEventType, TileButtonState, TileNumberColor


class TileButton(QPushButton):
  state: TileButtonState = TileButtonState.DEFAULT
  callback: Callable[[Qt.MouseButton, TileButtonState], None]

  def __init__(self, text: str, size: QSize, callback):
    super().__init__(text)

    self.setFixedSize(size)

    self.setStyleSheet("""
      font-size: 18px;
      padding: 5px 10px;
      background-color: #e0e0e0;
    """)

    self.callback = callback

  def set_text(self) -> None:
    match self.state:
      case TileButtonState.DEFAULT:
        self.setText('')
      case TileButtonState.FLAGGED:
        self.setText('m')
      case TileButtonState.QUESTION:
        self.setText('?')

  def mousePressEvent(self, event: QMouseEvent) -> None:
    state_before = self.state
    btn = event.button()
    if btn == Qt.RightButton:
      self.state = TileButtonState.next(self.state)
      self.set_text()

    state_after = self.state
    self.callback(btn, state_after, state_before)

    return super().mousePressEvent(event)


class Tile(QStackedWidget):
  size: QSize = QSize(40, 40)

  row: int
  col: int
  val: int

  revealed: bool = False
  protected: bool = False

  def __init__(self, row: int, col: int, val: int, callback):
    super().__init__()

    self.row = row
    self.col = col
    self.val = val

    self.callback = callback

    # set tile params
    self.setStyleSheet('background-color: #f0f0f0;')
    self.setFixedSize(self.size)

    label = QLabel(
      parent=self,
      text=str(val) if val > 0 else ('o' if val == -1 else ''),
      alignment=Qt.AlignCenter,
      size=self.size,
      styleSheet=(
        f'font-size: 18px; color: rgb{TileNumberColor.by_val(val).value}; font-weight: bold;' if val > 0 else ''
      ),
    )

    btn = TileButton('', self.size, self.handleMouseEvent)

    self.addWidget(label)
    self.addWidget(btn)

    self.setCurrentIndex(self.indexOf(btn))

  def handleMouseEvent(self, btn: Qt.MouseButton, state: TileButtonState, last_state: TileButtonState) -> None:
    match btn:
      case Qt.LeftButton:
        self.callback(TileEventType.OPENSINGLE, self)
      case Qt.MiddleButton:
        self.callback(TileEventType.OPENSQUARE, self)
      case Qt.RightButton:
        if last_state == TileButtonState.FLAGGED and state != TileButtonState.FLAGGED:
          self.protected = False
        elif state == TileButtonState.FLAGGED and last_state != TileButtonState.FLAGGED:
          self.protected = True

  def reveal_tile(self) -> None:
    self.revealed = True
    self.setCurrentIndex(self.currentIndex() - 1)


class GameHeader(QWidget):
  btn_restart: QPushButton
  lcd_mines: QLCDNumber
  lcd_timer: QLCDNumber

  stopwatch: QTimer

  def __init__(self):
    super().__init__()

    layout = QHBoxLayout(self)

    self.btn_restart = QPushButton(parent=self, text='Restart', size=QSize(150, 100))
    self.btn_restart.setFixedSize(150, 40)
    self.lcd_mines = QLCDNumber(parent=self, digitCount=3, size=QSize(100, 40), mode=QLCDNumber.Dec)
    self.lcd_timer = QLCDNumber(parent=self, digitCount=3, size=QSize(100, 40), mode=QLCDNumber.Dec)

    self.stopwatch = QTimer(parent=self, timeout=self.lcd_timer.display, interval=1000, singleShot=False)

    layout.addWidget(self.lcd_mines, 1, Qt.AlignLeft)
    layout.addWidget(self.btn_restart, 1, Qt.AlignCenter)
    layout.addWidget(self.lcd_timer, 1, Qt.AlignRight)

  def set_mines(self, mines: int) -> None:
    self.lcd_mines.display(mines)

  def start_timer(self) -> None:
    self.stopwatch.start()


class GameFrame(QFrame):
  header: QWidget
  grid: QWidget

  rows: int
  cols: int

  open_tiles: int = 0
  win_condition: int

  finish_callback: Callable[[bool], None]

  def __init__(self, finish_callback):
    super().__init__()

    self.setStyleSheet("""
      margin: 0px 0px;
      background-color: #f0f0f0f0;
    """)

    self.finish_callback = finish_callback

    layout = QVBoxLayout(self)

    # header = QWidget(parent=self, layout=QHBoxLayout())
    # for label, align in [('mines', Qt.AlignLeft), ('icon', Qt.AlignCenter), ('timer', Qt.AlignRight)]:
    #   header.layout().addWidget(QLabel(label, header), 1, align)

    self.header = GameHeader()
    self.grid = QWidget(parent=self, layout=QGridLayout())

    layout.addWidget(self.header)
    layout.addWidget(self.grid)

  def setup_grid(self, rows: int, cols: int, mines: int, matrix: list[list[int]]) -> None:
    self.rows = rows
    self.cols = cols
    self.win_condition = rows * cols - mines

    layout = self.grid.layout()
    for i in range(rows):
      for j in range(cols):
        layout.addWidget(Tile(i, j, matrix[i][j], self.handle_tile_event), i, j)

    self.setFixedSize((cols + 1) * 40, (rows + 1) * 40)
    self.header.set_mines(mines)

  def handle_tile_event(self, event: TileEventType, tile: Tile) -> None:
    match event:
      case TileEventType.OPENSINGLE:
        self.open_single_tile(tile)
      case TileEventType.OPENSQUARE:
        self.open_square(tile)
      case TileEventType.MARK:
        self

  def open_tile(self, tile: Tile):
    tile.reveal_tile()
    self.open_tiles += 1

    if tile.val == -1:
      self.finish_callback(False)
    elif self.open_tiles == self.win_condition:
      self.finish_callback(True)

  # simply open one tile
  def open_single_tile(self, tile: Tile) -> None:
    if tile.protected or tile.revealed:
      return

    self.open_tile(tile)

    if tile.val == 0:
      self.open_null_field(tile)

  # open tile at pos and all surrounding tiles
  def open_square(self, tile: Tile) -> None:
    pass

  # recursively open all tiles that have a 0 value and surrounding number tiles
  def open_null_field(self, tile) -> None:
    for i in range(-1, 2):
      for j in range(-1, 2):
        if i == 0 and j == 0:
          continue

        x = tile.row + i
        y = tile.col + j

        if x < 0 or x >= self.rows or y < 0 or y >= self.cols:
          continue

        self.open_single_tile(self.grid.layout().itemAtPosition(x, y).widget())
