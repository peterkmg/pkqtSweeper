import sys
from PySide6.QtWidgets import QApplication
from window import GameWindow


def main() -> None:
  app = QApplication(sys.argv)
  app.setApplicationName('pkqt Minesweeper')
  app.setStyle('Fusion')
  gw = GameWindow()
  gw.show()
  sys.exit(app.exec())


if __name__ == '__main__':
  main()
