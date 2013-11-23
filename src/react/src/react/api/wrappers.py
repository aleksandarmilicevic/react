class Wrapper(object):
    def __init__(self, target, robj=None, fname=None):
        self._target = target
        self._owner  = robj
        self._fname  = fname

    def unwrap(self):
        return self._target

    def append(self, *args, **kwargs):
        return self._handle_mutation_call('append', *args, **kwargs)

    def size(self): return self.__len__()

    def _handle_mutation_call(self, mname, *args, **kwargs):
        if not hasattr(self._target, mname):
            raise AttributeError(self._target, mname)
        ans = getattr(self._target, mname)(*args, **kwargs)
        if self._owner is not None:
            self._owner._field_mutated(self._fname, self._target)
        return ans

    def __len__(self):
        ftype = self._owner.meta().field(self._fname)
        if self._target is None:
            return 0
        elif ftype.is_scalar():
            return 1
        else:
            return len(self._target)

    def __iter__(self):
        ftype = self._owner.meta().field(self._fname)
        if self._target is None:
            pass
        elif ftype.is_scalar():
            yield self._target
        else:
            for x in self._target:
                yield x

    def __getattr__(self, name):
        return getattr(self._target, name)

    def __add__(self, other):
        if isinstance(other, Wrapper):
            other = other.unwrap()
        return Wrapper.wrap(self._target + other)

    def __eq__(self, other): return self.__bop__("eq", other)
    def __ne__(self, other): return self.__bop__("ne", other)
    def __gt__(self, other): return self.__bop__("gt", other)
    def __lt__(self, other): return self.__bop__("lt", other)
    def __ge__(self, other): return self.__bop__("ge", other)
    def __le__(self, other): return self.__bop__("le", other)

    def __str__(self): return str(self._target)
    def __repr__(self): return repr(self._target)

    def __bop__(self, op, other):
        if isinstance(other, Wrapper):
            other = other.unwrap()
        opname = "__%s__" % op
        return getattr(self.unwrap(), opname)(other)

    @staticmethod
    def wrap(*a, **kw):
        # return Wrapper(*a, **kw)
        return a[0]

def wrap(*a, **kw):
    return Wrapper.wrap(*a, **kw)

def unwrap(val):
    if isinstance(val, Wrapper):
        return val.unwrap()
    else:
        return val



