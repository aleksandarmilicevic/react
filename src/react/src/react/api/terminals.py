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

class CLITerminal(object):
    @staticmethod
    def react_config():
        print "configuring cli terminal"
        conf.cli = conf.E_THR_OPT.NEW_THR
