from typing import Callable
from game import Cfg, GameMode
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

    footer = QLabel('Created by PK', parent=self, styleSheet='font-size: 12px; color: black;', alignment=Qt.AlignCenter)

    layout.addWidget(header, 1)
    layout.addWidget(self.__main_btn_group)
    layout.addWidget(self.__mode_select_btn_group)
    layout.addWidget(footer, 1)

    self.__show_first_page(True)

  def __create_main_menu_group(self) -> QGroupBox:
    main_group = QGroupBox('Main Menu', parent=self)
    main_group.setFixedHeight(Cfg.menu_grp_height)
    main_group_layout = QVBoxLayout(main_group)

    btn_new_game = self.__make_button('New Game', lambda: self.__show_first_page(False))
    btn_exit = self.__make_button('Exit', lambda: QApplication.instance().quit())

    main_group_layout.addWidget(btn_new_game)
    main_group_layout.addWidget(btn_exit)

    return main_group

  def __create_mode_select_group(self, activate_game: Callable[[GameMode], None]) -> QGroupBox:
    mode_group = QGroupBox('Select difficulty')
    mode_group.setFixedHeight(Cfg.menu_grp_height)
    mode_group_layout = QVBoxLayout(mode_group)

    btn_start_beginner = self.__make_button('Beginner', lambda: activate_game(GameMode.BEGINNER))
    btn_start_intermediate = self.__make_button('Intermediate', lambda: activate_game(GameMode.INTERMEDIATE))
    btn_start_expert = self.__make_button('Expert', lambda: activate_game(GameMode.EXPERT))
    btn_back = self.__make_button('Back', lambda: self.__show_first_page(True))

    mode_group_layout.addWidget(btn_start_beginner)
    mode_group_layout.addWidget(btn_start_intermediate)
    mode_group_layout.addWidget(btn_start_expert)
    mode_group_layout.addWidget(btn_back)

    return mode_group

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
    self.__resize_window_callback(400, 400)
    self.__show_first_page(True)
