import curses
import react
from react import conf

LeftMargin = 50
TopMargin = 1

class CarSimCurses(object):

    def __init__(self, width, height):
        self.W = width
        self.H = height

    def start(self):
        self.stdscr = curses.initscr()
        self.win = curses.newpad(self.H+1, self.W+1)
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
        self.win.keypad(1)
        self.draw_border()

    def stop(self):
        curses.nocbreak()
        self.win.keypad(0)
        curses.echo()
        curses.curs_set(1)
        curses.endwin()

    def refresh(self):
        self.win.refresh(0,0, TopMargin,LeftMargin, TopMargin+self.H-1,LeftMargin+self.W-1)

    def draw_border(self):
        t, l = (TopMargin-1, LeftMargin-1)
        b, r = (TopMargin+self.H, LeftMargin+self.W)

        self.stdscr.addch(t, l, curses.ACS_ULCORNER)
        self.stdscr.addch(t, r, curses.ACS_URCORNER)
        self.stdscr.addch(b, l, curses.ACS_LLCORNER)
        self.stdscr.addch(b, r, curses.ACS_LRCORNER)

        for y in range(t+1, b):
            self.stdscr.addch(y, l, curses.ACS_VLINE)
            self.stdscr.addch(y, r, curses.ACS_VLINE)

        for x in range(l+1, r):
            self.stdscr.addch(t, x, curses.ACS_HLINE)
            self.stdscr.addch(b, x, curses.ACS_HLINE)
        
        self.stdscr.refresh()

    def clrscr(self):
        self.win.clear()
        self.refresh()

    def draw(self, draw_spec):
        self.win.clear()
        for name, x, y, color in draw_spec:
            if x >= 0 and y >= 0 and x < self.W and y < self.H:
                conf.trace("about to draw %s, %s, %s" % (y,x,name))
                self.win.addstr(y, x, name, curses.color_pair(color) | curses.A_STANDOUT)
        self.refresh()

def start(width, height):
    gui = CarSimCurses(width, height)
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

