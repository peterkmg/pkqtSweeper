from PySide6.QtWidgets import (
  QMainWindow,
  QVBoxLayout,
  QWidget,
  QSizePolicy,
  QMessageBox,
)


from game import GameState

from menu_frame import MenuFrame
from game_frame import GameFrame


class InfoBox(QMessageBox):
  def __init__(self, text: str, title: str, icon: QMessageBox.Icon):
    super().__init__()

    self.setText(text)
    self.setWindowTitle(title)
    self.setIcon(icon)
    self.setStandardButtons(QMessageBox.Ok)
    self.setDefaultButton(QMessageBox.Ok)


# create windows that has 2 frames
# one is menu frame where player can select to start the game or exit
# (and select game difficulty)
# another is game frame where the game is played
# menu frame is shown on the initial start of the game
class Window(QMainWindow):
  width: int = 400
  height: int = 400

  root: QWidget
  # root_layout: QLayout

  frame_menu: MenuFrame
  frame_game: GameFrame

  state: GameState

  def __init__(self):
    super().__init__()

    # set window title and size
    self.setWindowTitle('pkqt Minesweeper')
    # self.setFixedSize(self.width, self.height)
    self.setMinimumHeight(250)
    self.setMinimumWidth(250)
    self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

    self.root = QWidget(parent=self)
    layout = QVBoxLayout(self.root)

    # construct everything from bottom up
    self.frame_menu = MenuFrame(self.start_game)
    self.frame_menu.hide()

    self.frame_game = GameFrame(self.finish_game)
    self.frame_game.hide()

    layout.addWidget(self.frame_menu, 1)
    layout.addWidget(self.frame_game, 1)

    self.setCentralWidget(self.root)

    # show menu frame by default
    self.frame_menu.enable_main_menu()
    self.frame_menu.show()

  def start_game(self, mode):
    print(f'Starting game in mode {mode}')
    self.frame_menu.reset()

    self.state = GameState(mode)

    self.frame_menu.hide()
    self.frame_game.show()

    self.frame_game.setup_grid(self.state.rows, self.state.cols, self.state.mines, self.state.matrix)
    self.setFixedSize((self.state.cols + 1) * 40 + 20, (self.state.rows + 1) * 40 + 20)

  def finish_game(self, win: bool):
    msg = QMessageBox(
      parent=self,
      windowTitle='Game Ended',
      text=win and 'You won!' or 'You lost!',
      standardButtons=QMessageBox.Ok,
      defaultButton=QMessageBox.Ok,
      icon=QMessageBox.Information,
    )
    msg.exec()
