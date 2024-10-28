from typing import Callable
from game import TileEventType, TileButtonState, TileNumberColor, GameState, GameMode, Cfg
from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QMouseEvent
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


class TileButton(QPushButton):
  __slots__ = 'state'

  def __init__(self, text: str, parent: QWidget = None) -> None:
    super().__init__(text, parent)

    self.setFixedSize(QSize(Cfg.game_btn_height - 4, Cfg.game_btn_height - 4))
    self.state = TileButtonState.DEFAULT
    self.setStyleSheet("""
      font-size: 18px;
      padding: 5px 10px;
      background-color: #e0e0e0;
    """)

  def __decorate_button(self) -> None:
    match self.state:
      case TileButtonState.DEFAULT:
        self.setText('')
      case TileButtonState.FLAGGED:
        self.setText(Cfg.tile_txt_flagged)
      case TileButtonState.QUESTION:
        self.setText(Cfg.tile_txt_question)

  def cycle_state(self) -> None:
    self.state = TileButtonState.next(self.state)
    self.__decorate_button()

  # button hijacks left mouse clicks => propagate event to parent
  def mouseReleaseEvent(self, e: QMouseEvent) -> None:
    parent = self.parent()
    if parent and e.button() == Qt.LeftButton:
      QApplication.sendEvent(parent, e)
    return super().mouseReleaseEvent(e)


class Tile(QStackedWidget):
  __slots__ = (
    '__row',
    '__col',
    '__val',
    '__label',
    '__label_idx',
    '__btn',
    '__btn_idx',
    '__revealed',
    '__flagged',
    '__tile_event_callback',
  )

  def __init__(
    self, row: int, col: int, val: int, callback: Callable[[TileEventType, 'Tile'], None], parent: QWidget = None
  ) -> None:
    super().__init__(parent)

    self.__row = row
    self.__col = col
    self.__val = val
    self.__tile_event_callback = callback
    self.__revealed = False
    self.__flagged = False
    self.setStyleSheet('background-color: #f0f0f0;')
    self.setFixedSize(QSize(Cfg.game_btn_height, Cfg.game_btn_height))

    self.__label = QLabel(
      parent=self,
      text=str(val) if val > 0 else (Cfg.tile_txt_mine if val == -1 else ''),
      alignment=Qt.AlignCenter,
      styleSheet=(
        f'font-size: 18px; color: rgb{TileNumberColor.by_val(val).value}; font-weight: bold;'
        if val > 0
        else 'font-size: 18px;font-weight: bold;'
      ),
    )

    self.__btn = TileButton(text='', parent=self)

    self.addWidget(self.__label)
    self.addWidget(self.__btn)

    self.__label_idx = self.indexOf(self.__label)
    self.__btn_idx = self.indexOf(self.__btn)

    self.setCurrentIndex(self.__btn_idx)

  @property
  def row(self) -> int:
    return self.__row

  @property
  def col(self) -> int:
    return self.__col

  @property
  def val(self) -> int:
    return self.__val

  @property
  def flagged(self) -> bool:
    return self.__flagged

  @property
  def revealed(self) -> bool:
    return self.__revealed

  def mouseReleaseEvent(self, event: QMouseEvent) -> None:
    match event.button():
      case Qt.LeftButton:  # left click, only care if tile is not revealed or protected
        self.__tile_event_callback(TileEventType.OPENSINGLE, self)
      case Qt.MiddleButton:  # middle click, only care if tile is revealed
        self.__tile_event_callback(TileEventType.OPENSQUARE, self)
      case Qt.RightButton:  # right click, only care if tile is not revealed
        self.__tile_event_callback(TileEventType.MARK, self)

    return super().mousePressEvent(event)

  def change_mark(self) -> None:
    self.__btn.cycle_state()
    if self.__flagged and self.__btn.state != TileButtonState.FLAGGED:
      self.__flagged = False
    elif self.__btn.state == TileButtonState.FLAGGED and not self.__flagged:
      self.__flagged = True

  def reveal_tile(self) -> None:
    self.__revealed = True
    self.setCurrentIndex(self.__label_idx)


class GameHeader(QWidget):
  __slots__ = ('__lcd_mines', '__lcd_timer', '__stopwatch')

  def __init__(self, restart: Callable[[], None], activate_menu: Callable[[], None], parent: QWidget = None) -> None:
    super().__init__(parent)

    layout = QHBoxLayout(self)

    btn_menu = self.__make_button('Menu', activate_menu)
    btn_restart = self.__make_button('Restart', restart)

    self.__lcd_mines = QLCDNumber(
      parent=self, digitCount=3, size=QSize(Cfg.game_btn_width, Cfg.game_btn_height), mode=QLCDNumber.Dec
    )

    self.__lcd_timer = QLCDNumber(
      parent=self, digitCount=3, size=QSize(Cfg.game_btn_width, Cfg.game_btn_height), mode=QLCDNumber.Dec
    )

    self.__stopwatch = QTimer(
      parent=self,
      timeout=lambda: self.__lcd_timer.display(self.__lcd_timer.intValue() + 1),
      interval=1000,
      singleShot=False,
    )

    layout.addWidget(self.__lcd_mines, 1, Qt.AlignLeft)
    layout.addWidget(btn_menu, 1, Qt.AlignCenter)
    layout.addWidget(btn_restart, 1, Qt.AlignCenter)
    layout.addWidget(self.__lcd_timer, 1, Qt.AlignRight)

  def __make_button(self, text: str, callback: Callable) -> QPushButton:
    btn = QPushButton(parent=self, text=text, clicked=callback)
    btn.setFixedSize(Cfg.game_btn_width, Cfg.game_btn_height)
    btn.setStyleSheet('color: black;')
    return btn

  @property
  def mines(self) -> int:
    return self.__lcd_mines.intValue()

  @mines.setter
  def mines(self, value: int) -> None:
    self.__lcd_mines.display(value)

  def new_timer(self) -> None:
    self.__lcd_timer.display(0)
    self.__stopwatch.start()

  def halt_timer(self) -> int:
    self.__stopwatch.stop()
    return self.__lcd_timer.intValue()

  def decrement_mines(self) -> None:
    self.__lcd_mines.display(self.__lcd_mines.intValue() - 1)

  def increment_mines(self) -> None:
    self.__lcd_mines.display(self.__lcd_mines.intValue() + 1)


class GameFrame(QFrame):
  __slots__ = (
    '__header',
    '__grid',
    '__state',
    '__active',
    '__open_tiles',
    '__win_condition',
    '__resize_callback',
    '__finish_callback',
    '__open_queue',
  )

  def __init__(
    self,
    finish_callback: Callable[[int, int], None],
    resize_callback: Callable[[int, int], None],
    activate_menu: Callable[[], None],
    parent: QWidget = None,
  ) -> None:
    super().__init__(parent)

    self.setStyleSheet("""
      margin: 0px 0px;
      background-color: #f0f0f0f0;
    """)
    self.__open_queue: set[Tile] = set()
    self.__grid: QWidget = None
    self.__resize_callback = resize_callback
    self.__finish_callback = finish_callback
    self.__state = GameState()

    layout = QVBoxLayout(self)
    self.__header = GameHeader(self.__create_game, activate_menu, self)
    layout.addWidget(self.__header)

  def __render_grid(self) -> None:
    if self.__grid is not None:
      self.layout().removeWidget(self.__grid)
      self.__grid.deleteLater()

    self.__grid = QWidget(parent=self, layout=QGridLayout())
    self.layout().addWidget(self.__grid)

    self.__open_tiles = 0
    self.__win_condition = self.__state.rows * self.__state.cols - self.__state.mines

    layout: QGridLayout = self.__grid.layout()
    layout.setAlignment(Qt.AlignCenter)
    layout.setVerticalSpacing(0)
    layout.setHorizontalSpacing(0)
    layout.setContentsMargins(14, 0, 0, 0)
    layout.setSizeConstraint(QGridLayout.SetFixedSize)
    for i in range(self.__state.rows):
      for j in range(self.__state.cols):
        layout.addWidget(Tile(i, j, self.__state.matrix[i][j], self.__handle_tile_event, self.__grid), i, j)

    self.setFixedSize((self.__state.cols + 1) * Cfg.game_btn_height, (self.__state.rows + 1) * Cfg.game_btn_height)
    self.__header.mines = self.__state.mines
    self.__resize_callback((self.__state.cols + 1) * Cfg.game_btn_height, (self.__state.rows + 1) * Cfg.game_btn_height)
    self.__active = True
    self.__header.new_timer()

  def __create_game(self) -> None:
    self.__state.create_state()
    self.__render_grid()

  def __handle_tile_event(self, event: TileEventType, tile: Tile) -> None:
    if not self.__active:
      return

    match event:
      case TileEventType.OPENSINGLE:
        self.__process_tile(tile)
      case TileEventType.OPENSQUARE:
        self.__process_square(tile)
      case TileEventType.MARK:
        self.__process_mark(tile)

  def __open_tile(self, tile: Tile) -> None:
    tile.reveal_tile()
    self.__open_tiles += 1

    if tile.val == -1 or self.__open_tiles == self.__win_condition:
      self.__active = False
      self.__finish_callback(tile.val != -1, self.__header.halt_timer())

  def __process_tile(self, tile: Tile) -> None:
    if tile.flagged or tile.revealed:
      return

    self.__open_tile(tile)

    if tile.val == 0:
      self.__enqueue_adjacent(tile)

    self.__process_queue()

  def __process_square(self, tile: Tile) -> None:
    layout = self.__grid.layout()
    flagged = 0
    tiles = set()
    for i in range(-1, 2):
      for j in range(-1, 2):
        x = tile.row + i
        y = tile.col + j

        if x < 0 or x >= self.__state.rows or y < 0 or y >= self.__state.cols:
          continue

        if layout.itemAtPosition(x, y).widget().flagged:
          flagged += 1
        else:
          tiles.add(layout.itemAtPosition(x, y).widget())

    if flagged == tile.val:
      self.__open_queue = self.__open_queue.union(tiles)
      self.__process_queue()

  def __process_mark(self, tile: Tile) -> None:
    if not tile.revealed:
      flagged = tile.flagged
      tile.change_mark()
      if flagged and not tile.flagged:
        self.__header.increment_mines()
      elif not flagged and tile.flagged:
        self.__header.decrement_mines()

  def __enqueue_adjacent(self, tile) -> None:
    layout = self.__grid.layout()
    for i in range(-1, 2):
      for j in range(-1, 2):
        if i == 0 and j == 0:
          continue

        x = tile.row + i
        y = tile.col + j

        if x < 0 or x >= self.__state.rows or y < 0 or y >= self.__state.cols:
          continue

        self.__open_queue.add(layout.itemAtPosition(x, y).widget())

  def __process_queue(self) -> None:
    while self.__open_queue:
      tile = self.__open_queue.pop()
      self.__process_tile(tile)

  def activate(self, mode: GameMode) -> None:
    self.__state.mode = mode
    self.__create_game()
