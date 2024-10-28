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
  QApplication,
)
from PySide6.QtGui import QMouseEvent

from game import TileEventType, TileButtonState, TileNumberColor, GameState, GameMode

import emoji


class TileButton(QPushButton):
  size: QSize = QSize(36, 36)
  state: TileButtonState = TileButtonState.DEFAULT

  def __init__(self, text: str, parent: QWidget = None):
    super().__init__(text, parent=parent)

    self.setFixedSize(self.size)
    self.setMouseTracking(False)

    self.setStyleSheet("""
      font-size: 18px;
      padding: 5px 10px;
      background-color: #e0e0e0;
    """)

  def decorate_button(self) -> None:
    match self.state:
      case TileButtonState.DEFAULT:
        self.setText('')
      case TileButtonState.FLAGGED:
        self.setText('🚩')
      case TileButtonState.QUESTION:
        self.setText('❓')

  def cycle_state(self) -> None:
    self.state = TileButtonState.next(self.state)
    self.decorate_button()

  # button hijacks left mouse clicks => propagate event to parent
  def mouseReleaseEvent(self, e: QMouseEvent) -> None:
    parent = self.parent()
    if parent and e.button() == Qt.LeftButton:
      QApplication.sendEvent(parent, e)
    return super().mouseReleaseEvent(e)


class Tile(QStackedWidget):
  size: QSize = QSize(40, 40)

  row: int
  col: int
  val: int

  label: QLabel
  label_idx: int
  btn: TileButton
  btn_idx: int

  revealed: bool = False
  flagged: bool = False

  tile_event_callback: Callable[[TileEventType, 'Tile'], None]

  def __init__(self, row: int, col: int, val: int, callback: Callable[[TileEventType, 'Tile'], None]):
    super().__init__()

    self.row = row
    self.col = col
    self.val = val

    self.tile_event_callback = callback

    # set tile params
    self.setStyleSheet('background-color: #f0f0f0;')
    self.setFixedSize(self.size)

    self.label = QLabel(
      parent=self,
      text=str(val) if val > 0 else ('💥' if val == -1 else ''),
      alignment=Qt.AlignCenter,
      size=self.size,
      styleSheet=(
        val > 0
        and f'font-size: 18px; color: rgb{TileNumberColor.by_val(val).value}; font-weight: bold;'
        or 'font-size: 18px;font-weight: bold;'
      ),
    )

    self.btn = TileButton('', parent=self)

    self.addWidget(self.label)
    self.addWidget(self.btn)

    self.label_idx = self.indexOf(self.label)
    self.btn_idx = self.indexOf(self.btn)

    self.setCurrentIndex(self.btn_idx)

  # attach event handler to tile to avoid processing mouse events on any other widgets we don't care about
  def mouseReleaseEvent(self, event: QMouseEvent) -> None:
    match event.button():
      case Qt.LeftButton:  # left click, only care if tile is not revealed or protected
        self.tile_event_callback(TileEventType.OPENSINGLE, self)
      case Qt.MiddleButton:  # middle click, only care if tile is revealed
        self.tile_event_callback(TileEventType.OPENSQUARE, self)
      case Qt.RightButton:  # right click, only care if tile is not revealed
        self.tile_event_callback(TileEventType.MARK, self)

    return super().mousePressEvent(event)

  def change_mark(self) -> None:
    self.btn.cycle_state()
    if self.flagged and self.btn.state != TileButtonState.FLAGGED:
      self.flagged = False
    elif self.btn.state == TileButtonState.FLAGGED and not self.flagged:
      self.flagged = True

  def reveal_tile(self) -> None:
    self.revealed = True
    self.setCurrentIndex(self.label_idx)


class GameHeader(QWidget):
  lcd_mines: QLCDNumber
  lcd_timer: QLCDNumber

  stopwatch: QTimer

  restart_callback: Callable[[], None]

  def __init__(self, restart_callback: Callable[[], None], activate_menu_callback: Callable[[], None]):
    super().__init__()

    layout = QHBoxLayout(self)

    btn_menu = QPushButton(parent=self, text='Menu', clicked=activate_menu_callback)
    btn_menu.setFixedSize(100, 40)
    btn_restart = QPushButton(parent=self, text='Restart', clicked=restart_callback)
    btn_restart.setFixedSize(100, 40)

    self.lcd_mines = QLCDNumber(parent=self, digitCount=3, size=QSize(100, 40), mode=QLCDNumber.Dec)
    self.lcd_timer = QLCDNumber(parent=self, digitCount=3, size=QSize(100, 40), mode=QLCDNumber.Dec)

    self.stopwatch = QTimer(
      parent=self,
      timeout=lambda: self.lcd_timer.display(self.lcd_timer.intValue() + 1),
      interval=1000,
      singleShot=False,
    )

    layout.addWidget(self.lcd_mines, 1, Qt.AlignLeft)
    layout.addWidget(btn_menu, 1, Qt.AlignCenter)
    layout.addWidget(btn_restart, 1, Qt.AlignCenter)
    layout.addWidget(self.lcd_timer, 1, Qt.AlignRight)

  def set_mines(self, mines: int) -> None:
    self.lcd_mines.display(mines)

  def new_timer(self) -> None:
    self.lcd_timer.display(0)
    self.stopwatch.start()

  def halt_timer(self) -> int:
    self.stopwatch.stop()
    return self.lcd_timer.intValue()

  def decrement_mines(self) -> None:
    self.lcd_mines.display(self.lcd_mines.intValue() - 1)

  def increment_mines(self) -> None:
    self.lcd_mines.display(self.lcd_mines.intValue() + 1)


class GameFrame(QFrame):
  header: GameHeader
  grid: QWidget = None

  state: GameState

  active: bool = False
  open_tiles: int
  win_condition: int

  resize_callback: Callable[[int, int], None]
  finish_callback: Callable[[bool], None]
  activate_menu_frame: Callable[[], None]

  open_queue: set[Tile] = set()

  def __init__(
    self,
    finish_callback: Callable[[int, int], None],
    resize_callback: Callable[[int, int], None],
    activate_menu_frame: Callable[[], None],
  ):
    super().__init__()

    self.setStyleSheet("""
      margin: 0px 0px;
      background-color: #f0f0f0f0;
    """)

    self.resize_callback = resize_callback
    self.finish_callback = finish_callback
    self.activate_menu_frame = activate_menu_frame

    self.state = GameState()

    layout = QVBoxLayout(self)
    self.header = GameHeader(self.create_game, activate_menu_frame)
    layout.addWidget(self.header)

  def activate(self, mode: GameMode) -> None:
    self.state.set_mode(mode)
    self.create_game()

  def render_grid(self) -> None:
    if self.grid is not None:
      self.layout().removeWidget(self.grid)
      self.grid.deleteLater()

    self.grid = QWidget(parent=self, layout=QGridLayout())
    self.layout().addWidget(self.grid)

    self.rows = self.state.rows
    self.cols = self.state.cols

    self.open_tiles = 0
    self.win_condition = self.state.rows * self.state.cols - self.state.mines

    layout = self.grid.layout()
    for i in range(self.state.rows):
      for j in range(self.state.cols):
        layout.addWidget(Tile(i, j, self.state.matrix[i][j], self.handle_tile_event), i, j)

    self.setFixedSize((self.state.cols + 1) * 40, (self.state.rows + 1) * 40)
    self.header.set_mines(self.state.mines)
    self.resize_callback((self.state.cols + 1) * 40, (self.state.rows + 1) * 40)
    self.active = True
    self.header.new_timer()

  def create_game(self) -> None:
    self.state.create_state()
    self.render_grid()

  def handle_tile_event(self, event: TileEventType, tile: Tile) -> None:
    if not self.active:
      return

    match event:
      case TileEventType.OPENSINGLE:
        self.process_tile(tile)
      case TileEventType.OPENSQUARE:
        self.process_square(tile)
      case TileEventType.MARK:
        self.process_mark(tile)

  def open_tile(self, tile: Tile) -> None:
    tile.reveal_tile()
    self.open_tiles += 1

    if tile.val == -1 or self.open_tiles == self.win_condition:
      self.active = False
      self.finish_callback(tile.val != -1, self.header.halt_timer())

  def process_tile(self, tile: Tile) -> None:
    if tile.flagged or tile.revealed:
      return

    self.open_tile(tile)

    if tile.val == 0:
      self.enqueue_adjacent(tile)

    self.process_queue()

  def process_square(self, tile: Tile) -> None:
    # only process if value is equal to number of flagged adjacent tiles
    layout = self.grid.layout()
    flagged = 0
    tiles = set()
    for i in range(-1, 2):
      for j in range(-1, 2):
        x = tile.row + i
        y = tile.col + j

        if x < 0 or x >= self.rows or y < 0 or y >= self.cols:
          continue

        if layout.itemAtPosition(x, y).widget().flagged:
          flagged += 1
        else:
          tiles.add(layout.itemAtPosition(x, y).widget())

    if flagged == tile.val:
      self.open_queue = self.open_queue.union(tiles)
      self.process_queue()

  def process_mark(self, tile: Tile) -> None:
    if not tile.revealed:
      flagged = tile.flagged
      tile.change_mark()
      if flagged and not tile.flagged:
        self.header.increment_mines()
      elif not flagged and tile.flagged:
        self.header.decrement_mines()

  def enqueue_adjacent(self, tile) -> None:
    layout = self.grid.layout()
    for i in range(-1, 2):
      for j in range(-1, 2):
        if i == 0 and j == 0:
          continue

        x = tile.row + i
        y = tile.col + j

        if x < 0 or x >= self.rows or y < 0 or y >= self.cols:
          continue

        self.open_queue.add(layout.itemAtPosition(x, y).widget())

  def process_queue(self) -> None:
    while self.open_queue:
      tile = self.open_queue.pop()
      self.process_tile(tile)
