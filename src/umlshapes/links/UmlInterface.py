
from logging import Logger
from logging import getLogger

from wx import PENSTYLE_SHORT_DASH

from wx import MemoryDC
from wx import Pen

from wx.lib.ogl import ARROW_ARROW

from pyutmodelv2.PyutLink import PyutLink

from umlshapes.links.UmlLink import UmlLink
from umlshapes.shapes.UmlClass import UmlClass


class UmlInterface(UmlLink):

    def __init__(self, pyutLink: PyutLink, interfaceClass: UmlClass, implementingClass: UmlClass):
        """

        Args:
            pyutLink:
            interfaceClass:
            implementingClass:
        """

        self.interfaceLogger: Logger = getLogger(__name__)

        super().__init__(pyutLink=pyutLink)

        self.AddArrow(type=ARROW_ARROW)

        self._interfaceClass:    UmlClass = interfaceClass
        self._implementingClass: UmlClass = implementingClass

    def OnDraw(self, dc: MemoryDC):

        pen: Pen = dc.GetPen()
        pen.SetStyle(PENSTYLE_SHORT_DASH)
        self.SetPen(pen)

        super().OnDraw(dc=dc)
