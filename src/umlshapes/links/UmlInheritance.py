
from logging import Logger
from logging import getLogger

from wx.lib.ogl import ARROW_ARROW

from pyutmodelv2.PyutLink import PyutLink

from umlshapes.links.UmlLink import UmlLink
from umlshapes.shapes.UmlClass import UmlClass


class UmlInheritance(UmlLink):
    """
    Inheritance

    srcId == SubClass
    dstId == Base Class.  (arrow here)
    """
    def __init__(self, pyutLink: PyutLink, baseClass: UmlClass, subClass: UmlClass):
        """

        Args:
            pyutLink:
            baseClass:
            subClass:
        """
        super().__init__(pyutLink=pyutLink)

        self.inheritanceLogger: Logger = getLogger(__name__)

        self._baseClass: UmlClass = baseClass
        self._subClass:  UmlClass = subClass

        self.AddArrow(type=ARROW_ARROW)

    @property
    def baseClass(self) -> UmlClass:
        return self._baseClass

    @baseClass.setter
    def baseClass(self, baseClass: UmlClass):
        self._baseClass = baseClass

    @property
    def subClass(self) -> UmlClass:
        return self._subClass

    @subClass.setter
    def subClass(self, subClass: UmlClass):
        self._subClass = subClass

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self):
        baseClass:   UmlClass = self.baseClass
        subClass:    UmlClass = self.subClass
        baseClassId: int      = baseClass.id
        subClassId:  int      = subClass.id

        return f'UmlInheritance[id: {subClassId} {subClass} inherits from: id: {baseClassId} {baseClass}]'
