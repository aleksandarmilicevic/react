class RecordBase(object):
    def __init__(self, **kwargs):
        pass

    def meta(self): return type(self).__metaclass__
