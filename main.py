import sys

from PySide6.QtWidgets import QApplication

from window import Window


# making minesweeper game
def main():
  app = QApplication(sys.argv)
  app.setApplicationName('pkqt Minesweeper')
  window = Window()
  window.show()
  sys.exit(app.exec())


if __name__ == '__main__':
  main()
