class combomethod(object):
    """
    Credit:
    http://stackoverflow.com/questions/2589690/creating-a-method-that-is-simultaneously-an-instance-and-class-method
    """
    def __init__(self, method):
        self.method = method

    def __get__(self, obj=None, objtype=None):
        @functools.wraps(self.method)
        def _wrapper(*args, **kwargs):
            if obj is not None:
                return self.method(obj, *args, **kwargs)
            else:
                return self.method(objtype, *args, **kwargs)
        return _wrapper

class curry:
    """
    Allows function currying.

    Credit:
    http://jonathanharrington.wordpress.com/2007/11/01/currying-and-python-a-practical-example
    """
    def __init__(self, fun, *args, **kwargs):
        self.fun = fun
        self.pending = args[:]
        self.kwargs = kwargs.copy()

    def __call__(self, *args, **kwargs):
        self._update_args(*args, **kwargs)
        return self.fun(*self.pending, **self.kwargs)

    def __getitem__(self, *args, **kwargs):
        self._update_args(*args, **kwargs)

    def _update_args(self, *args, **kwargs):
        if kwargs and self.kwargs:
            kw = self.kwargs.copy()
            kw.update(kwargs)
        else:
            kw = kwargs or self.kwargs
        self.pending = self.pending + args
        self.kwargs = kw

def enum(*vals, **kvals):
    enums = {}
    for val in vals:
        for e in val.split(" "):
            enums[e] = e
    for k, v in kvals.iteritems():
        enums[k] = v
    return type('Enum', (), enums)
