import sys
from PySide6.QtWidgets import QApplication
from window import GameWindow


def main() -> None:
  """Main entry point for the pkqt Minesweeper game."""
  app = QApplication(sys.argv)
  app.setApplicationName('pkqt Minesweeper')
  gw = GameWindow()
  gw.show()
  sys.exit(app.exec())


if __name__ == '__main__':
  main()
