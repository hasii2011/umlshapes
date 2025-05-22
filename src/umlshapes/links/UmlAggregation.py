
from logging import Logger
from logging import getLogger

from pyutmodelv2.PyutLink import PyutLink

from wx import MemoryDC
from wx import BLACK_BRUSH

from umlshapes.links.UmlAssociation import UmlAssociation


class UmlAggregation(UmlAssociation):
    def __init__(self, pyutLink: PyutLink):

        super().__init__(pyutLink=pyutLink)
        self.aggregationLogger: Logger = getLogger(__name__)

    def OnDraw(self, dc: MemoryDC):

        super().OnDraw(dc=dc)

        self.SetBrush(BLACK_BRUSH)

        self._drawDiamond(dc=dc, filled=True)
