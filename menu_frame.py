from typing import Callable
from game_utils import Cfg, GameMode
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QGroupBox, QPushButton, QApplication
from PySide6.QtCore import Qt


class MenuFrame(QFrame):
  __slots__ = ('__resize_window_callback', '__main_btn_group', '__mode_select_btn_group')

  def __init__(self, resize_window: Callable[[int, int], None], activate_game: Callable[[GameMode], None]) -> None:
    super().__init__()

    self.setStyleSheet("""
      background-color: #f0f0f0;
      margin: 0px 15px;
    """)

    self.__resize_window_callback = resize_window

    layout = QVBoxLayout(self)

    header = QLabel(
      'Minesweeper Game',
      alignment=Qt.AlignCenter,
      parent=self,
      styleSheet="""
        font-size: 24px;
        font-weight: bold;
        color: black;
      """,
    )

    self.__main_btn_group = self.__create_main_menu_group()
    self.__mode_select_btn_group = self.__create_mode_select_group(activate_game)

    footer = QLabel('by pk', parent=self, styleSheet='font-size: 12px; color: black;', alignment=Qt.AlignCenter)

    layout.addWidget(header, 1)
    layout.addWidget(self.__main_btn_group)
    layout.addWidget(self.__mode_select_btn_group)
    layout.addWidget(footer, 1)

    self.__show_first_page(True)

  def __create_main_menu_group(self) -> QGroupBox:
    main_group = self.__make_group('Main Menu')
    layout = main_group.layout()

    btn_new_game = self.__make_button('New Game', lambda: self.__show_first_page(False))
    btn_exit = self.__make_button('Exit', lambda: QApplication.instance().quit())

    layout.addWidget(btn_new_game)
    layout.addWidget(btn_exit)

    return main_group

  def __create_mode_select_group(self, activate_game: Callable[[GameMode], None]) -> QGroupBox:
    mode_group = self.__make_group('Select Mode')
    layout = mode_group.layout()

    btn_start_beginner = self.__make_button('Beginner', lambda: activate_game(GameMode.BEGINNER))
    btn_start_intermediate = self.__make_button('Intermediate', lambda: activate_game(GameMode.INTERMEDIATE))
    btn_start_expert = self.__make_button('Expert', lambda: activate_game(GameMode.EXPERT))
    btn_back = self.__make_button('Back', lambda: self.__show_first_page(True))

    layout.addWidget(btn_start_beginner)
    layout.addWidget(btn_start_intermediate)
    layout.addWidget(btn_start_expert)
    layout.addWidget(btn_back)

    return mode_group

  def __make_group(self, title: str) -> QGroupBox:
    grp = QGroupBox(title, parent=self, layout=QVBoxLayout())
    grp.setFixedHeight(Cfg.menu_grp_height)
    grp.setStyleSheet('color: black;')
    return grp

  def __make_button(self, text: str, callback: Callable) -> QPushButton:
    btn = QPushButton(
      parent=self,
      text=text,
      clicked=callback,
    )
    btn.setStyleSheet('color: black;')
    btn.setFixedHeight(Cfg.menu_btn_height)
    return btn

  def __show_first_page(self, flag: bool) -> None:
    self.__main_btn_group.setHidden(not flag)
    self.__mode_select_btn_group.setHidden(flag)

  def activate(self) -> None:
    self.__resize_window_callback(Cfg.menu_win_size, Cfg.menu_win_size)
    self.__show_first_page(True)
