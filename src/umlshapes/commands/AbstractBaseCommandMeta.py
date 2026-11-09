from abc import ABCMeta

from wx.siplib import wrappertype


class AbstractBaseCommandMeta(ABCMeta, wrappertype):
    """
    Metaclass resolving the conflict between ABCMeta and wx.siplib.wrappertype.
    """
    pass
