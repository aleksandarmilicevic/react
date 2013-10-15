import abc
import operator as op
import react

class Type(object):
    __metaclass__ = abc.ABCMeta

    @staticmethod
    def get(t):
        if isinstance(t, Type):   return t
        elif isinstance(t, type): return react.api.types.RefType(t)
        elif isinstance(t, str):  return react.api.types.UnresolvedType(t)
        elif isinstance(t, list): return react.api.types.ProductType(*t)
        else: raise RuntimeError("Cannot convert %s to Type" % t)

    @abc.abstractmethod
    def arity(self): pass

    @abc.abstractmethod
    def column(self, idx): pass

    def utypes(self): return [self.column(i) for i in range(self.arity())]
    def domain(self): return self.column(0)
    def range(self):  return self.column(self.arity() - 1)

class UType(Type):
    __metaclass__ = abc.ABCMeta

    def __init__(self, cls): self._cls = cls

    def cls(self):           return self._cls
    def arity(self):         return 1
    def column(self, idx):   assert idx == 0; return self
    
class ProductType(Type):
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, *children): self._children = [Type.get(ch) for ch in children]

    def children(self):    return self._children
    def arity(self):       return sum([ch.arity() for ch in self.children()])
    def utypes(self):      return reduce(op.add, [ch.utypes() for ch in self.children()])
    def column(self, idx): return self.utypes()[idx]

class ModType(Type):
    __metaclass__ = abc.ABCMeta

    def __init__(self, sub): self._sub = Type.get(sub)

    def sub(self):          return self._sub
    def arity(self):        return self.sub().arity()
    def column(self, idx):  return self.sub().column(idx)

class RefType(UType):
    def __init__(self, cls): super(RefType, self).__init__(cls)
    def __str__(self):       return self.cls().__name__

class UnresolvedType(UType):
    def __init__(self, string): super(RefType, self).__init__(string)
    def __str__(self):          return self.cls()
    
class SetType(ModType):
    def __init__(self, sub): super(SetType, self).__init__(sub)
    def __str__(self):       return "set<%s>" % self.sub()

class ListType(ModType):
    def __init__(self, sub): super(ListType, self).__init__(sub)
    def __str__(self):       return "list<%s>" % self.sub()

class DictType(ProductType):
    def __init(self, lhs, rhs): super(DictType, self).__init__(lhs, rhs)
    def __str__(self):          return "dict<%s,%s>" % (self.domain(), self.range())

def setof(t):    return SetType(t)
def listof(t):   return ListType(t)
def dictof(k,v): return DictType(k, v)
