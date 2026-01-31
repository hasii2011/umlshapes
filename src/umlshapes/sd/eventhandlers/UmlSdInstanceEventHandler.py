
from logging import Logger
from logging import getLogger

from wx import ClientDC

from umlshapes.lib.ogl import ShapeEvtHandler

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.sd.UmlSDInstance import UmlSDInstance

from umlshapes.types.UmlDimensions import UmlDimensions

from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler


class UmlSdInstanceEventHandler(UmlBaseEventHandler):

    def __init__(self, umlSdInstance: UmlSDInstance, umlPubSubEngine: IUmlPubSubEngine, previousEventHandler: ShapeEvtHandler):

        self.logger: Logger = getLogger(__name__)

        super().__init__(previousEventHandler=previousEventHandler, shape=umlSdInstance)
        self._umlPubSubEngine = umlPubSubEngine

    def OnEndSize(self, x, y):
        """
        We want to tell the lifeline to stretch to shrink to new size

        Args:
            x:
            y:
        """
        from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine

        umlSDInstance: UmlSDInstance = self.GetShape()
        umlSDLifeLIne: UmlSDLifeLine = umlSDInstance.umlSDLifeLine

        umlSDLifeLIne.adjustLifeLineTopPosition()

        super().OnEndSize(x, y)

    def OnDrawOutline(self, dc: ClientDC, x: int, y: int, w: int, h: int):
        """
        Called when shape is moving or is resized
        Need to override base because:
            Composite shape returns floats (sometimes);
            TODO: I need to fix y for sequence diagrams

        Args:
            dc:  This is a client DC; It won't draw on OS X
            x:  x position of center of shape
            y:  y position of center of shape
            w:  shape width
            h:  shape height
        """
        from umlshapes.ShapeTypes import UmlShapeGenre

        umlShape: UmlShapeGenre = self.GetShape()
        umlShape.Move(dc=dc, x=x, y=y, display=True)

        umlShape.size = UmlDimensions(width=round(w), height=round(h))
        umlShape.umlFrame.refresh()
