from menu_frame import MenuFrame
from game_frame import GameFrame
from game import Cfg
from PySide6.QtWidgets import (
  QMainWindow,
  QVBoxLayout,
  QWidget,
  QMessageBox,
)


class GameWindow(QMainWindow):
  __slots__ = ('__root', '__frame_menu', '__frame_game')

  def __init__(self) -> None:
    super().__init__()
    self.setWindowTitle('pkqt Minesweeper')
    self.setStyleSheet('background-color: #f0f0f0;')

    self.__root = QWidget(parent=self)
    layout = QVBoxLayout(self.__root)

    self.__frame_menu = MenuFrame(self.__resize_window, self.__activate_game_frame)
    self.__frame_game = GameFrame(self.__finish_game, self.__resize_window, self.__activate_menu_frame)

    layout.addWidget(self.__frame_menu, 1)
    layout.addWidget(self.__frame_game, 1)

    self.setCentralWidget(self.__root)
    self.__activate_menu_frame()

  def __activate_menu_frame(self) -> None:
    self.__frame_menu.show()
    self.__frame_game.hide()
    self.__frame_menu.activate()

  def __activate_game_frame(self, mode: str) -> None:
    self.__frame_menu.hide()
    self.__frame_game.show()
    self.__frame_game.activate(mode)

  def __resize_window(self, width: int, height: int) -> None:
    self.setFixedSize(width + Cfg.wind_hrz_offset, height + Cfg.wind_vrt_offset)

  def __finish_game(self, win: bool, time: int) -> None:
    msg = f'You won!\nFinished in {time} seconds!' if win else 'Boom! You lost!'
    icon = QMessageBox.Information if win else QMessageBox.Critical

    QMessageBox(
      parent=self,
      windowTitle='Game Ended',
      text=msg,
      standardButtons=QMessageBox.Ok,
      defaultButton=QMessageBox.Ok,
      icon=icon,
      styleSheet='font-size: 13px; color: black;',
    ).exec()
