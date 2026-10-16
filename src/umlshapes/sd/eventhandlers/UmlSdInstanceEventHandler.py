
from typing import Optional
from typing import cast

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
        self._umlPubSubEngine: IUmlPubSubEngine = umlPubSubEngine
        self._fixedY: Optional[int] = None
        self._fixedMouseY: Optional[int] = None

    def OnBeginDragLeft(self, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Record the baseline Y position so the instance is constrained strictly
        to horizontal dragging.

        Args:
            x:
            y:
            keys:
            attachment:
        """
        from umlshapes.ShapeTypes import UmlShapeGenre

        umlShape: UmlShapeGenre = cast(UmlShapeGenre, self.GetShape())
        self._fixedY = round(umlShape.GetY())
        self._fixedMouseY = y
        super().OnBeginDragLeft(x, y, keys, attachment)

    def OnDragLeft(self, draw: bool, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Lock Y to the fixed baseline mouse Y so that movement and deltaXY are
        strictly horizontal.

        Args:
            draw:
            x:
            y:
            keys:
            attachment:
        """
        from umlshapes.ShapeTypes import UmlShapeGenre

        if self._fixedMouseY is None:
            self._fixedMouseY = y
            umlShape: UmlShapeGenre = cast(UmlShapeGenre, self.GetShape())
            self._fixedY = round(umlShape.GetY())

        super().OnDragLeft(draw, x, self._fixedMouseY, keys, attachment)

    def OnEndDragLeft(self, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Finalize the horizontal-only drag by locking the release Y coordinate to
        the initial mouse baseline Y.

        Args:
            x:
            y:
            keys:
            attachment:
        """
        lockedY: int = self._fixedMouseY if self._fixedMouseY is not None else y
        super().OnEndDragLeft(x, lockedY, keys, attachment)
        self._fixedY = None
        self._fixedMouseY = None

    def OnEndSize(self, x: int, y: int):
        """
        We want to tell the lifeline to stretch or shrink to new size

        Args:
            x:
            y:
        """
        from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine

        umlSDInstance: UmlSDInstance = cast(UmlSDInstance, self.GetShape())
        umlSDLifeLine: UmlSDLifeLine = umlSDInstance.umlSDLifeLine

        umlSDLifeLine.adjustLifeLineTopPosition()

        super().OnEndSize(x, y)

    def OnDrawOutline(self, dc: ClientDC, x: int, y: int, w: int, h: int):
        """
        Called when shape is moving or is resized. Enforce the fixed baseline Y
        position so the instance never drifts vertically.

        Args:
            dc:  This is a client DC; It won't draw on OS X
            x:  x position of center of shape
            y:  y position of center of shape
            w:  shape width
            h:  shape height
        """
        from umlshapes.ShapeTypes import UmlShapeGenre

        umlShape: UmlShapeGenre = cast(UmlShapeGenre, self.GetShape())
        targetY: int = self._fixedY if self._fixedY is not None else round(umlShape.GetY())
        umlShape.Move(dc=dc, x=x, y=targetY, display=True)

        umlShape.size = UmlDimensions(width=round(w), height=round(h))
        umlShape.umlFrame.refresh()

