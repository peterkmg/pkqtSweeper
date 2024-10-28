from typing import Callable
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QGroupBox, QPushButton, QLayout, QApplication
from PySide6.QtCore import Qt, QSize

from game import GameMode


# class MenuButton(QPushButton):
#   def __init__(self, text: str, height: int, callback):
#     super().__init__(text)

#     self.setFixedHeight(height)
#     self.clicked.connect(callback)

#     self.setStyleSheet("""
#       font-size: 18px;
#       padding: 5px 10px;
#     """)


class MenuFrame(QFrame):
  btn_size: QSize = QSize(200, 180)
  btn_height: int = 40
  btn_group_size: int = 250

  main_btn_group: QGroupBox
  mode_select_btn_group: QGroupBox

  resize_window_callback: Callable[[int, int], None]

  def __init__(self, resize_window: Callable[[int, int], None], activate_game: Callable[[GameMode], None]):
    super().__init__()

    self.setStyleSheet("""
      background-color: #f0f0f0;
      margin: 0px 15px;
    """)

    self.resize_window_callback = resize_window

    layout = QVBoxLayout(self)

    header = QLabel(
      'Minesweeper Game',
      alignment=Qt.AlignCenter,
      parent=self,
      styleSheet="""
      font-size: 24px;
      font-weight: bold;
    """,
    )

    # main menu
    main_group = QGroupBox('Main Menu', parent=self)
    main_group.setFixedHeight(self.btn_group_size)
    main_group_layout = QVBoxLayout(main_group)

    btn_new_game = self.make_button('New Game', self.btn_height, lambda: self.show_first_page(False))
    btn_exit = self.make_button('Exit', self.btn_height, lambda: QApplication.instance().quit())

    main_group_layout.addWidget(btn_new_game)
    main_group_layout.addWidget(btn_exit)

    self.main_btn_group = main_group

    # game mode selection
    mode_group = QGroupBox('Select difficulty')
    mode_group.setFixedHeight(self.btn_group_size)
    mode_group_layout = QVBoxLayout(mode_group)

    btn_start_beginner = self.make_button('Beginner', self.btn_height, lambda: activate_game(GameMode.BEGINNER))
    btn_start_intermediate = self.make_button(
      'Intermediate', self.btn_height, lambda: activate_game(GameMode.INTERMEDIATE)
    )
    btn_start_expert = self.make_button('Expert', self.btn_height, lambda: activate_game(GameMode.EXPERT))
    btn_back = self.make_button('Back', self.btn_height, lambda: self.show_first_page(True))

    mode_group_layout.addWidget(btn_start_beginner)
    mode_group_layout.addWidget(btn_start_intermediate)
    mode_group_layout.addWidget(btn_start_expert)
    mode_group_layout.addWidget(btn_back)
    self.mode_select_btn_group = mode_group

    ## footer
    footer = QLabel('Created by PK', parent=self, styleSheet='font-size: 12px;', alignment=Qt.AlignCenter)

    # populate layout
    layout.addWidget(header, 1)
    layout.addWidget(main_group)
    layout.addWidget(mode_group)
    layout.addWidget(footer, 1)

    self.show_first_page(True)

  def make_button(self, text: str, height: int, callback: Callable) -> QPushButton:
    btn = QPushButton(
      parent=self,
      text=text,
      clicked=callback,
    )
    btn.setFixedHeight(height)
    return btn

  def activate(self):
    self.resize_window_callback(400, 400)
    self.show_first_page(True)

  def show_first_page(self, flag: bool):
    self.main_btn_group.setHidden(not flag)
    self.mode_select_btn_group.setHidden(flag)
