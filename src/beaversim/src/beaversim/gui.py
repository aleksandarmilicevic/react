import curses
import react
from react import conf

class BeaverSimCurses(object):
    def __init__(self):
        pass

    def __enter__(self):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(1)

    def __exit__(self, *a):
        self.stdscr.refresh()
        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.echo()
        curses.endwin()

    def stop(self):
        self.__exit__()

    def clrscr(self):
        self.stdscr.clear()

    def draw(self, lst):
        for b in lst:
            print b

def start():
    gui = BeaverSimCurses()
    gui.__enter__()
    gui.clrscr()
    return gui

# import pygtk
# pygtk.require('2.0')
# import gtk

# class BeaverSimGUI(object):
#     def __init__(self):
#         self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
#         self.window.show()

# def start():
#     BeaverSimGUI()

# from PyQt4 import QtGui
# BeaverQtApp = QtGui.QApplication([])

# def start():
#     w = QtGui.QWidget()
#     w.resize(250, 150)
#     w.move(300, 300)
#     w.setWindowTitle("hi")
#     w.show()

