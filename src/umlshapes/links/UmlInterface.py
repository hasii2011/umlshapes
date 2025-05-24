
from logging import Logger
from logging import getLogger

from wx import MemoryDC

from wx.lib.ogl import ARROW_ARROW

from pyutmodelv2.PyutLink import PyutLink
from wx.lib.ogl import LineShape

from umlshapes.UmlUtils import UmlUtils
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

        assert dc is not None, 'Where is my DC'

        if self._linkName is None:
            self._linkName = self._createLinkName()
            self._setupAssociationLabel(umlAssociationLabel=self._linkName)

        if self.Selected() is True:
            self.SetPen(UmlUtils.redDashedPen())
        else:
            self.SetPen(UmlUtils.blackDashedPen())
        # Hack:
        #       I want to skip the UmlLink OnDraw so this line will be drawn
        LineShape.OnDraw(self=self, dc=dc)

    def __repr__(self):
        return f'UmlInterface - {super().__repr__()}'
