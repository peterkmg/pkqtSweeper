from typing import Callable
from game_utils import TileEventType, TileButtonState, TileNumberColor, Board, GameMode, Cfg
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
    '__neighbors',
  )

  def __init__(
    self, row: int, col: int, callback: Callable[[TileEventType, 'Tile'], None], parent: QWidget = None
  ) -> None:
    super().__init__(parent)

    self.__row = row
    self.__col = col
    self.__val = 0
    self.__tile_event_callback = callback
    self.__revealed = False
    self.__flagged = False
    self.setStyleSheet('background-color: #f0f0f0;')
    self.setFixedSize(QSize(Cfg.game_btn_height, Cfg.game_btn_height))

    self.__label = QLabel(parent=self, text='', alignment=Qt.AlignCenter)
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

  @val.setter
  def val(self, value: int) -> None:
    self.__val = value

  @property
  def flagged(self) -> bool:
    return self.__flagged

  @property
  def revealed(self) -> bool:
    return self.__revealed

  @property
  def neighbors(self) -> list['Tile']:
    return self.__neighbors

  @neighbors.setter
  def neighbors(self, value: list['Tile']) -> None:
    self.__neighbors = value

  def init(self) -> None:
    self.__label.setText(Cfg.tile_txt_mine if self.__val == -1 else str(self.__val))
    self.__label.setStyleSheet(
      'font-size: 18px; font-weight: bold;'
      if self.__val == -1
      else f'color: rgb{TileNumberColor.by_val(self.__val).value}; font-size: 18px; font-weight: bold;'
    )

  def increment_value(self) -> None:
    if self.__val == -1:
      return
    self.__val += 1

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

  def reveal(self) -> None:
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

  @property
  def time(self) -> int:
    return self.__lcd_timer.intValue()

  @time.setter
  def time(self, value: int) -> None:
    self.__lcd_timer.display(value)

  def start_timer(self) -> None:
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
    '__board',
    '__tiles',
    '__active',
    '__active_tiles',
    '__first_click',
    '__open_tiles',
    '__win_condition',
    '__game_won',
    '__game_lost',
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

    self.setStyleSheet('background-color: #f0f0f0f0;')
    self.__open_queue: set[Tile] = set()
    self.__active = False
    self.__grid: QWidget = None
    self.__resize_callback = resize_callback
    self.__finish_callback = finish_callback

    layout = QVBoxLayout(self)
    layout.setAlignment(Qt.AlignTop)
    layout.setContentsMargins(5, 0, 20, 0)
    self.__header = GameHeader(self.__init_game, activate_menu, self)
    layout.addWidget(self.__header)

  def __init_params(self) -> None:
    self.__first_click = True
    self.__open_tiles = 0
    self.__game_won = False
    self.__game_lost = False
    self.__win_condition = self.__board.rows * self.__board.cols - self.__board.mines
    self.__active_tiles: set[Tile] = set()

  def __init_header(self) -> None:
    self.__header.mines = self.__board.mines
    self.__header.time = 0

  def __init_grid(self) -> None:
    if self.__grid is not None:
      self.layout().removeWidget(self.__grid)
      self.__grid.deleteLater()

    self.__grid = QWidget(parent=self, layout=QGridLayout())
    self.layout().addWidget(self.__grid)

    layout: QGridLayout = self.__grid.layout()
    layout.setAlignment(Qt.AlignCenter)
    layout.setVerticalSpacing(0)
    layout.setHorizontalSpacing(0)
    layout.setContentsMargins(8, 0, 0, 0)
    layout.setSizeConstraint(QGridLayout.SetFixedSize)
    self.setFixedSize((self.__board.cols + 1) * Cfg.game_btn_height, (self.__board.rows + 2) * Cfg.game_btn_height)

  def __init_tiles(self) -> None:
    self.__init_grid()
    layout: QGridLayout = self.__grid.layout()

    tiles = [
      [Tile(i, j, self.__handle_tile_event, self.__grid) for j in range(self.__board.cols)]
      for i in range(self.__board.rows)
    ]

    for row in tiles:
      for t in row:
        t.neighbors = [tiles[i][j] for i, j in self.__board.get_neighbors(t.row, t.col)]
        layout.addWidget(t, t.row, t.col)

    self.__tiles = tiles

  def __init_game(self) -> None:
    self.__init_params()
    self.__init_tiles()
    self.__init_header()
    self.__resize_callback((self.__board.cols + 1) * Cfg.game_btn_height, (self.__board.rows + 2) * Cfg.game_btn_height)
    self.__active = True

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

  def __reveal_tile(self, tile: Tile) -> None:
    if tile.flagged or tile.revealed:
      return

    tile.reveal()
    self.__open_tiles += 1

    if tile.val == -1:
      self.__game_lost = True
    elif self.__open_tiles == self.__win_condition:
      self.__game_won = True

    if tile.val == 0:
      self.__enqueue_adjacent(tile)

    self.__process_queue()

  def __process_tile(self, tile: Tile) -> None:
    if self.__first_click:
      self.__handle_first_click(tile)

    if tile.flagged or tile.revealed:
      return

    self.__reveal_tile(tile)
    self.__post_process_tile()

  def __post_process_tile(self) -> None:
    if not self.__game_lost and not self.__game_won:
      return

    self.__active = False
    if self.__game_lost:
      for row in self.__tiles:
        for t in row:
          if t.val == -1:
            t.reveal()

    self.__finish_callback(not self.__game_lost, self.__header.halt_timer())

  def __process_square(self, tile: Tile) -> None:
    if not tile.revealed or tile.val == 0:
      return

    mines = 0
    for t in tile.neighbors:
      if t.flagged:
        mines += 1

    if mines == tile.val:
      for t in tile.neighbors:
        if not t.flagged and not t.revealed:
          self.__reveal_tile(t)

    self.__post_process_tile()

  def __process_mark(self, tile: Tile) -> None:
    if not tile.revealed:
      flagged = tile.flagged
      tile.change_mark()
      if flagged and not tile.flagged:
        self.__header.increment_mines()
      elif not flagged and tile.flagged:
        self.__header.decrement_mines()

  def __enqueue_adjacent(self, tile) -> None:
    for t in tile.neighbors:
      if not t.revealed:
        self.__open_queue.add(t)

  def __process_queue(self) -> None:
    while self.__open_queue:
      tile = self.__open_queue.pop()
      self.__reveal_tile(tile)

  def __handle_first_click(self, tile: Tile) -> None:
    self.__first_click = False
    self.__board.calc_mine_placement(tile.row, tile.col)

    for r, c in self.__board.mine_placement:
      self.__tiles[r][c].val = -1
      self.__active_tiles.add(self.__tiles[r][c])
      for t in self.__tiles[r][c].neighbors:
        t.increment_value()
        self.__active_tiles.add(t)

    for t in self.__active_tiles:
      t.init()

    self.__header.start_timer()

  def activate(self, mode: GameMode) -> None:
    self.__board = Board(mode)
    self.__init_game()
