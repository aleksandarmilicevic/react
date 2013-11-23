import curses
import react
from react import conf

class BeaverSimCurses(object):
    def __init__(self):
        pass

    def start(self):
        self.stdscr = curses.initscr()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.stdscr.keypad(1)

    def stop(self):
        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.echo()
        curses.curs_set(1)
        curses.endwin()

    def clrscr(self):
        self.stdscr.clear()
        self.stdscr.refresh()

    def draw(self, draw_spec):
        self.stdscr.clear()
        for name, x, y, color in draw_spec:
            conf.trace("about to draw %s, %s, %s" % (type(y), type(x), type(name)))
            self.stdscr.addstr(y, x, name, curses.color_pair(color))
        self.stdscr.refresh()

def start():
    gui = BeaverSimCurses()
    gui.start()
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

