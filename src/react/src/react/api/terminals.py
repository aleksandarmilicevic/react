import curses
import curses.ascii
import thread
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
        self.key_consts = filter(lambda k: k.startswith("KEY_"), curses.__dict__.keys())
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

    def on_exit(self):
        curses.nocbreak()
        curses.echo()
        curses.curs_set(1)
        self.stdscr.keypad(0)
        curses.endwin()

    def read_spin(self, new_thr=True):
         if new_thr:
             thread.start_new_thread(self.thr_func, ())
         else:
             self.thr_func()

    def thr_func(self):
        while 1:
            c = self.stdscr.getch()
            mth_name = "on_KEY_%s" % self.transl_ch(c)
            if hasattr(self, mth_name):
                getattr(self, mth_name)()
            elif hasattr(self, "on_KEY"):
                getattr(self, "on_KEY")(c)

    def transl_ch(self, ch):
        conf.trace("translating ch %d", ch)
        if curses.ascii.isalnum(ch):
            conf.trace("returning %s", curses.ascii.unctrl(ch))
            return curses.ascii.unctrl(ch)
        else:
            for key in self.key_consts:
                if ch == getattr(curses, key):
                    conf.trace("returning %s", key[4:])
                    return key[4:]
            conf.trace("could not translate %d", ch)
            return str(ch)

class CLITerminal(object):
    @staticmethod
    def react_config():
        print "configuring cli terminal"
        conf.cli = conf.E_THR_OPT.NEW_THR
