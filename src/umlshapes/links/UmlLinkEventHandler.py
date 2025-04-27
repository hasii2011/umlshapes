
from logging import Logger
from logging import getLogger

from wx import ClientDC
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
