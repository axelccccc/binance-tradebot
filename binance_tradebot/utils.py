import sys, itertools
from importlib import import_module



def igetattr(obj, attr):
    """Case Insensitive version of `getattr()`"""
    for a in dir(obj):
        if a.lower() == attr.lower():
            return getattr(obj, a)



def instantiate(module: str, class_name: str, *args):
    """Instantiate class from str name (case insensitive)"""
    module = import_module(module)
    class_ = igetattr(module, class_name)
    instance = class_(*args)
    return instance


def is_subclass_of(subclass_name: str, class_):
    """Verifies the class_ has a subclass with the name sublass_name (Case Insensitive)"""

    available = [a.__name__.lower() for a in class_.__subclasses__()]
    if not available.count(subclass_name):
        return False
    return True

def are_subclass_of(subclass_names: list, class_):
    """Verifies that the subclass names are all from subclasses of class_ (Case Insensitive)"""

    available = [a.__name__.lower() for a in class_.__subclasses__()]

    for subclass_name in subclass_names:
        if not available.count(subclass_name.lower()):
            return False
    return True