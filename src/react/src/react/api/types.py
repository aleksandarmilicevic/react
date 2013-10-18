import abc
import operator as op
import react

class Type(object):
    """
    Abstract class.

    Represents a generic notion of a multi-arity type.  Used to denote
    types of fields that ReactObjs contain.
    """
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

    @abc.abstractmethod
    def default_value(self): pass

    def utypes(self): return [self.column(i) for i in range(self.arity())]
    def domain(self): return self.column(0)
    def range(self):  return self.column(self.arity() - 1)

class UType(Type):
    """
    Abstract representation of a unary type.

    @attr _cls: object; the actual underlying type
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, cls): self._cls = cls

    def cls(self):           return self._cls
    def arity(self):         return 1
    def column(self, idx):   assert idx == 0; return self
    def default_value(self): return None
    
class ProductType(Type):
    """
    Abstract representation of a product type.

    @attr _children: list<Type>; components of this product type.  Components
                                 don't have to be unary types.
    """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, *children): self._children = [Type.get(ch) for ch in children]

    def children(self):    return self._children
    def arity(self):       return sum([ch.arity() for ch in self.children()])
    def utypes(self):      return reduce(op.add, [ch.utypes() for ch in self.children()])
    def column(self, idx): return self.utypes()[idx]

class ModType(Type):
    """
    Abstract wrapper class adding a modifier to another type

    @attr _sub: Type; wrapped React Type
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, sub): self._sub = Type.get(sub)

    def sub(self):          return self._sub
    def arity(self):        return self.sub().arity()
    def column(self, idx):  return self.sub().column(idx)

class RefType(UType):
    """
    A unary type wrapping a python's type

    @attr _cls: type; wrapped python type
    """
    def __init__(self, cls): super(RefType, self).__init__(cls)
    def __str__(self):       return self.cls().__name__
    def default_value(self): 
        if self.cls() == str:    return ""
        elif self.cls() == int:  return 0
        elif self.cls() == bool: return false
        else:                    return None

class UnresolvedType(UType):
    """
    A unary type wrapping a string (unresolved type)

    @attr _cls: str; wrapped string
    """
    def __init__(self, string): super(RefType, self).__init__(string)
    def __str__(self):          return self.cls()
    def default_value(self):    return None

class SetType(ModType):
    """
    A mod type denoting a set of another (wrapped) type
    """
    def __init__(self, sub): super(SetType, self).__init__(sub)
    def __str__(self):       return "set<%s>" % self.sub()
    def default_value(self):    return set()

class ListType(ModType):
    """
    A mod type denoting a list of another (wrapped) type
    """    
    def __init__(self, sub): super(ListType, self).__init__(sub)
    def __str__(self):       return "list<%s>" % self.sub()
    def default_value(self): return list()

class DictType(ProductType):
    """
    A binary type denoting a dictionary of another two types.
    
    @attr _lhs: Type; key type
    @attr _rhs: Type; value type
    """
    def __init(self, lhs, rhs): super(DictType, self).__init__(lhs, rhs)
    def __str__(self):          return "dict<%s,%s>" % (self.domain(), self.range())
    def lhs(self):              return self.children()[0]
    def rhs(self):              return self.children()[1]
    def default_value(self):    return dict()

def setof(t):    return SetType(t)
def listof(t):   return ListType(t)
def dictof(k,v): return DictType(k, v)
