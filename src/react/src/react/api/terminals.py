import curses
from react import conf
from react.utils import curry

class CursesTerminal(object):
    @classmethod
    def react_config(cls):
        print "configuring curses terminal"
        conf.cli   = conf.E_THR_OPT.FALSE
        fname = "%s.log" % cls.__name__
        file_logger = curry(conf.E_LOGGER.FILE, fname)
        conf.log   = curry(conf._prepend, "[LOG]   ", file_logger)
        conf.debug = curry(conf._prepend, "[DEBUG] ", file_logger)
        conf.trace = curry(conf._prepend, "[TRACE] ", file_logger)
        conf.warn  = curry(conf._prepend, "[WARN]  ", file_logger)
        conf.error = curry(conf._prepend, "[ERROR] ", file_logger)

    def on_start(self):
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

    def on_exit(self):
        curses.nocbreak()
        curses.echo()
        curses.curs_set(1)
        curses.endwin()
    

class CLITerminal(object):
    @staticmethod
    def react_config():
        print "configuring cli terminal"
        conf.cli = conf.E_THR_OPT.NEW_THR
