from PySide6.QtWidgets import (
  QMainWindow,
  QVBoxLayout,
  QWidget,
  QMessageBox,
)

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


class GameWindow(QMainWindow):
  root: QWidget

  frame_menu: MenuFrame
  frame_game: GameFrame

  def __init__(self):
    super().__init__()

    # set window title and size
    self.setWindowTitle('pkqt Minesweeper')

    self.root = QWidget(parent=self)
    layout = QVBoxLayout(self.root)

    self.frame_menu = MenuFrame(self.resize_window, self.activate_game_frame)
    self.frame_game = GameFrame(self.finish_game, self.resize_window, self.activate_menu_frame)

    layout.addWidget(self.frame_menu, 1)
    layout.addWidget(self.frame_game, 1)

    self.setCentralWidget(self.root)

    # show menu frame by default
    self.activate_menu_frame()

  def activate_menu_frame(self) -> None:
    self.frame_menu.show()
    self.frame_game.hide()
    self.frame_menu.activate()

  def activate_game_frame(self, mode) -> None:
    self.frame_menu.hide()
    self.frame_game.show()
    self.frame_game.activate(mode)

  def resize_window(self, width: int, height: int) -> None:
    self.setFixedSize(width + 20, height + 20)

  def finish_game(self, win: bool, time: int) -> None:
    msg = QMessageBox(
      parent=self,
      windowTitle='Game Ended',
      text=win and f'You won!\nFinished in {time} seconds!' or 'Boom! You lost!',
      standardButtons=QMessageBox.Ok,
      defaultButton=QMessageBox.Ok,
      icon=win and QMessageBox.Information or QMessageBox.Critical,
    )
    msg.exec()
