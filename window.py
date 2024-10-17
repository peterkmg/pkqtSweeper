from PySide6.QtWidgets import (
  QApplication,
  QMainWindow,
  QLayout,
  QLabel,
  QGroupBox,
  QPushButton,
  QFrame,
  QVBoxLayout,
  QHBoxLayout,
  QGridLayout,
  QStackedLayout,
  QWidget,
)

from PySide6.QtCore import Qt, QSize

from game import GameMode, GameState, TileNumberColor


class MenuButton(QPushButton):
  def __init__(self, text: str, height: int, callback):
    super().__init__(text)

    self.setFixedHeight(height)
    self.clicked.connect(callback)

    self.setStyleSheet("""
      font-size: 18px;
      padding: 5px 10px;
    """)


class MenuFrame(QFrame):
  menu_layout: QLayout

  main_group: QGroupBox
  main_group_layout: QLayout
  mode_group: QGroupBox
  mode_group_layout: QLayout

  btn_size: int = 40
  btn_group_size: int = 250

  def __init__(self, start_callback):
    super().__init__()

    self.setStyleSheet("""
      background-color: #f0f0f0;
                       margin: 0px 15px;
    """)

    layout = QVBoxLayout()

    # header, positioned at the top aligned to the center vertically and horizontally
    header = QLabel('Minesweeper Game')
    header.setStyleSheet("""
      font-size: 24px;
      font-weight: bold;
    """)
    header.setAlignment(Qt.AlignCenter)
    layout.addWidget(header, 1)

    # main menu
    main_group = QGroupBox('Main Menu')
    main_group.setFixedHeight(self.btn_group_size)

    main_group_layout = QVBoxLayout()
    btn_new_game = MenuButton('New Game', self.btn_size, self.click_new_game)
    main_group_layout.addWidget(btn_new_game)
    btn_exit = MenuButton('Exit', self.btn_size, self.click_exit)
    btn_exit.clicked.connect(self.click_exit)
    main_group_layout.addWidget(btn_exit)
    main_group.setLayout(main_group_layout)
    main_group.setHidden(True)  # hide everything by default

    self.main_group_layout = main_group_layout
    self.main_group = main_group

    # game mode selection
    mode_group = QGroupBox('Select difficulty')
    mode_group.setFixedHeight(self.btn_group_size)

    mode_group_layout = QVBoxLayout()

    btn_start_beginner = MenuButton('Beginner', self.btn_size, lambda: start_callback(GameMode.BEGINNER))
    btn_start_intermediate = MenuButton('Intermediate', self.btn_size, lambda: start_callback(GameMode.INTERMEDIATE))
    btn_start_expert = MenuButton('Expert', self.btn_size, lambda: start_callback(GameMode.EXPERT))
    btn_back = MenuButton('Back', self.btn_size, self.click_back)

    mode_group_layout.addWidget(btn_start_beginner)
    mode_group_layout.addWidget(btn_start_intermediate)
    mode_group_layout.addWidget(btn_start_expert)
    mode_group_layout.addWidget(btn_back)

    mode_group.setLayout(mode_group_layout)
    mode_group.setHidden(True)  # hide everything by default

    self.mode_group_layout = mode_group_layout
    self.mode_group = mode_group

    layout.addWidget(main_group)
    layout.addWidget(mode_group)

    footer = QLabel('Created by PK')
    footer.setAlignment(Qt.AlignCenter)

    layout.addWidget(footer, 1)

    self.setLayout(layout)

    self.menu_layout = layout

  def enable_main_menu(self):
    self.main_group.setHidden(False)

  def disable_main_menu(self):
    self.main_group.setHidden(True)

  def enable_mode_selection(self):
    self.mode_group.setHidden(False)

  def disable_mode_selection(self):
    self.mode_group.setHidden(True)

  def click_new_game(self):
    self.disable_main_menu()
    self.enable_mode_selection()

  def click_exit(self):
    QApplication.quit()

  def click_back(self):
    self.enable_main_menu()
    self.disable_mode_selection()

  def reset(self):
    self.enable_main_menu()
    self.disable_mode_selection()


class GameFrame(QFrame):
  game_layout: QLayout

  header: QWidget
  header_layout: QLayout

  grid: QWidget
  grid_layout: QLayout

  def __init__(self):
    super().__init__()

    layout = QVBoxLayout(self)

    header = QWidget(self)
    header_layout = QHBoxLayout(header)
    header_layout.addWidget(QLabel('mines', header))
    header_layout.addWidget(QLabel('icon', header))
    header_layout.addWidget(QLabel('timer', header))
    self.header = header

    layout.addWidget(header)

    grid = QWidget(self)
    grid_layout = QGridLayout(parent=grid, spacing=1, alignment=Qt.AlignCenter)
    # grid_layout.setAlignment(Qt.AlignCenter)
    # grid_layout.setSpacing(1)
    grid_layout.setContentsMargins(0, 0, 0, 0)
    self.grid_layout = grid_layout

    grid.setLayout(grid_layout)
    self.grid = grid

    layout.addWidget(grid)

    # self.setLayout(layout)

    self.game_layout = layout

  def setup_grid(self, rows: int, cols: int, matrix: list[list[int]], callback):
    for i in range(rows):
      for j in range(cols):
        self.grid_layout.addWidget(Tile(i, j, matrix[i][j], callback), i, j)

    self.grid.setLayout(self.grid_layout)


class Tile(QWidget):
  row: int
  col: int
  val: int

  index: int = 1
  layout: QLayout

  size: QSize = QSize(40, 40)

  def __init__(self, row: int, col: int, val: int, callback):
    super().__init__()

    self.row = row
    self.col = col
    self.val = val

    layout = QStackedLayout(self)
    self.layout = layout

    layout.addWidget(
      QLabel(
        parent=self,
        text=str(val) if val > 0 else '',
        alignment=Qt.AlignCenter,
        size=self.size,
        styleSheet=(
          f'font-size: 18px; color: rgb{TileNumberColor.by_val(val).value}; font-weight: bold;' if val > 0 else ''
        ),
      )
    )

    layout.addWidget(
      QPushButton(
        parent=self,
        size=self.size,
        styleSheet='background-color: #f0f0f0;',
        clicked=lambda: self.click_btn(callback),
      )
    )

    layout.setCurrentIndex(self.index)

  def open_tile(self, callback):
    self.layout.setCurrentIndex(0)
    callback(self.row, self.col, self.val)


# create windows that has 2 frames
# one is menu frame where player can select to start the game or exit
# (and select game difficulty)
# another is game frame where the game is played
# menu frame is shown on the initial start of the game
class Window(QMainWindow):
  width: int = 400
  height: int = 400

  root: QWidget
  root_layout: QLayout

  frame_menu: MenuFrame
  frame_game: GameFrame

  state: GameState

  def __init__(self):
    super().__init__()

    # set window title and size
    self.setWindowTitle('pkqt Minesweeper')
    self.setFixedSize(self.width, self.height)

    root = QWidget()

    # construct everything from bottom up
    self.frame_menu = MenuFrame(self.start_game)
    self.frame_menu.hide()

    self.frame_game = GameFrame()
    self.frame_game.hide()

    layout = QVBoxLayout()

    layout.addWidget(self.frame_menu, 1)
    layout.addWidget(self.frame_game, 1)

    root.setLayout(layout)
    self.root_layout = layout

    self.setCentralWidget(root)

    self.root = root

    # show menu frame by default
    self.frame_menu.enable_main_menu()
    self.frame_menu.show()

  def start_game(self, mode):
    print(f'Starting game in mode {mode}')
    self.frame_menu.reset()

    self.state = GameState(mode)

    self.frame_menu.hide()
    self.frame_game.show()

    self.frame_game.setup_grid(self.state.rows, self.state.cols, self.state.matrix, self.open_tile)

  def open_tile(self, row, col, val):
    print(f'Opening tile at {row}, {col} with value {val}')
