
from logging import Logger
from logging import getLogger

from pyutmodelv2.PyutLink import PyutLink
from wx import MemoryDC
from wx.core import BLACK_BRUSH
from wx.core import BLACK_PEN

from wx.lib.ogl import ARROW_FILLED_CIRCLE

from umlshapes.links.UmlAssociation import UmlAssociation
from umlshapes.types.Common import SOURCE_CARDINALITY_IDX


class UmlComposition(UmlAssociation):
    def __init__(self, pyutLink: PyutLink):

        super().__init__(pyutLink=pyutLink)
        self.compositionLogger: Logger = getLogger(__name__)

        # self.AddArrow(type=ARROW_FILLED_CIRCLE)

    def OnDraw(self, dc: MemoryDC):

        super().OnDraw(dc=dc)

        self.SetBrush(BLACK_BRUSH)

        x, y = self.GetLabelPosition(SOURCE_CARDINALITY_IDX)

        self._drawDiamond(dc=dc, filled=True)
