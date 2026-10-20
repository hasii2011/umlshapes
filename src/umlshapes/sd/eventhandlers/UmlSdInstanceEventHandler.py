from typing import Optional
from typing import cast

from logging import Logger
from logging import getLogger

from wx import ClientDC

from umlshapes.lib.ogl import ControlPoint
from umlshapes.lib.ogl import ShapeEvtHandler

from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.sd.UmlSDInstance import UmlSDInstance

from umlshapes.types.UmlDimensions import UmlDimensions

from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler

MIN_BASE_LIFELINE_LENGTH: int = 80
MIN_LIFELINE_BOTTOM_PADDING: int = 30


class UmlSdInstanceEventHandler(UmlBaseEventHandler):

    def __init__(self, umlSdInstance: UmlSDInstance, umlPubSubEngine: IUmlPubSubEngine, previousEventHandler: ShapeEvtHandler):

        self.logger: Logger = getLogger(__name__)

        super().__init__(previousEventHandler=previousEventHandler, shape=umlSdInstance)
        self._preferences:     UmlPreferences   = UmlPreferences()
        self._umlPubSubEngine: IUmlPubSubEngine = umlPubSubEngine
        self._fixedY:          Optional[int]    = None
        self._fixedMouseY:     Optional[int]    = None

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
        lockedY: int
        if self._fixedMouseY is not None:
            lockedY = self._fixedMouseY
        else:
            lockedY = y

        super().OnEndDragLeft(x, lockedY, keys, attachment)
        self._fixedY = None
        self._fixedMouseY = None

    def OnSizingBeginDragLeft(self, pt: ControlPoint, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Begin interactive sizing of the lifeline.

        Args:
            pt:
            x:
            y:
            keys:
            attachment:
        """
        self.logger.debug(f'OnSizingBeginDragLeft ({x}, {y})')

    def OnSizingDragLeft(self, pt: ControlPoint, draw: bool, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Interactively adjust the lifeline length during drag.

        Args:
            pt:
            draw:
            x:
            y:
            keys:
            attachment:
        """
        umlSDInstance: UmlSDInstance = cast(UmlSDInstance, self.GetShape())
        headerBottomY: int = round(umlSDInstance.umlSDLifeLine.rectangle.top)
        rawLength: int = y - headerBottomY

        minAllowedLength: int = self._computeMinAllowedLifeLineLength(umlSDInstance=umlSDInstance)
        newLength: int
        if rawLength < minAllowedLength:
            newLength = minAllowedLength
        else:
            newLength = rawLength

        if self._preferences.uniformLifeLineLength:
            umlSDInstance.umlFrame.setAllLifeLinesLength(newLength)
        else:
            umlSDInstance.setLifeLineLength(newLength)
            umlSDInstance.umlFrame.refresh()

    def OnSizingEndDragLeft(self, pt: ControlPoint, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Finalize interactive sizing of the lifeline.

        Args:
            pt:
            x:
            y:
            keys:
            attachment:
        """
        umlSDInstance: UmlSDInstance = cast(UmlSDInstance, self.GetShape())
        headerBottomY: int = round(umlSDInstance.umlSDLifeLine.rectangle.top)
        rawLength: int = y - headerBottomY

        minAllowedLength: int = self._computeMinAllowedLifeLineLength(umlSDInstance=umlSDInstance)
        newLength: int
        if rawLength < minAllowedLength:
            newLength = minAllowedLength
        else:
            newLength = rawLength

        if self._preferences.uniformLifeLineLength:
            umlSDInstance.umlFrame.setAllLifeLinesLength(newLength)
        else:
            umlSDInstance.setLifeLineLength(newLength)
            umlSDInstance.umlFrame.refresh()

    def _computeMinAllowedLifeLineLength(self, umlSDInstance: UmlSDInstance) -> int:
        from umlshapes.sd.UmlSDMessage import UmlSDMessage

        maxMessageY: int = 0
        targetInstances: list[UmlSDInstance]
        if self._preferences.uniformLifeLineLength:
            targetInstances = umlSDInstance.umlFrame.getSDInstances()
        else:
            targetInstances = [umlSDInstance]

        for instance in targetInstances:
            for line in instance.umlSDLifeLine.GetLines():
                if isinstance(line, UmlSDMessage):
                    messageBottom: int = max(line.fromY, line.toY)
                    if messageBottom > maxMessageY:
                        maxMessageY = messageBottom

        headerBottomY: int = round(umlSDInstance.umlSDLifeLine.rectangle.top)
        requiredLength: int = (maxMessageY - headerBottomY) + MIN_LIFELINE_BOTTOM_PADDING
        if requiredLength < MIN_BASE_LIFELINE_LENGTH:
            return MIN_BASE_LIFELINE_LENGTH
        return requiredLength

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
        targetY: int
        if self._fixedY is not None:
            targetY = self._fixedY
        else:
            targetY = round(umlShape.GetY())

        umlShape.Move(dc=dc, x=x, y=targetY, display=True)

        umlShape.size = UmlDimensions(width=round(w), height=round(h))
        umlShape.umlFrame.refresh()
