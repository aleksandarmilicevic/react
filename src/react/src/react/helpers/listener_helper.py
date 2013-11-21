import react
from react.api.model import ReactObj

class ListenerHelper:
    def lstner(self, *args):
        if not hasattr(self, "accesses"):
            self.accesses = []
        self.accesses.append(args)

    def reg_lstner(self):
        self.accesses = []
        ReactObj.add_access_listener(self.lstner)

    def unreg_lstner(self):
        ReactObj.remove_access_listener(self.lstner)

    def filter_accesses(self, col, val): return filter(lambda t: t[col] == val, self.accesses)
    def read_accesses(self):   return self.filter_accesses(0, "read")
    def write_accesses(self):  return self.filter_accesses(0, "write")

    @staticmethod
    def select_col(col, lst):  return map(lambda x: x[col], lst)
    def read_fld_names(self):  return self.select_col(2, self.read_accesses())
    def write_fld_names(self): return self.select_col(2, self.write_accesses())

