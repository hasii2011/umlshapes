
from logging import Logger
from logging import getLogger

from wx import ClientDC
from wx import DC

from wx.lib.ogl import ShapeCanvas
from wx.lib.ogl import ShapeEvtHandler

from umlshapes.links.UmlLink import UmlLink


class UmlLinkEventHandler(ShapeEvtHandler):

    def __init__(self, umlLink: UmlLink):

        self.logger: Logger = getLogger(__name__)

        super().__init__(shape=umlLink)

    def OnLeftClick(self, x: int, y: int, keys=0, attachment=0):

        self.logger.info(f'({x},{y}), {keys=} {attachment=}')

        umlLink: UmlLink = self.GetShape()

        canvas: ShapeCanvas = umlLink.GetCanvas()
        dc:     ClientDC    = ClientDC(canvas)

        canvas.PrepareDC(dc)

        umlLink.Select(select=True, dc=dc)

        middle = umlLink.GetLabelPosition(0)
        start  = umlLink.GetLabelPosition(1)
        end    = umlLink.GetLabelPosition(2)

        self.logger.info(f'{middle=} {start=} {end=}')

        controlPoints = umlLink.GetLineControlPoints()
        self.logger.info(f'{controlPoints=}')

        self.logger.info(f'{umlLink.GetNumberOfTextRegions()=}')

    def OnDrawControlPoints(self, dc):

        super().OnDrawControlPoints(dc=dc)
        # self.logger.info(f'Here we are')
