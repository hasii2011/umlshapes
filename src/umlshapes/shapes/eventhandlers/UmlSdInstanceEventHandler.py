
from typing import cast

from logging import Logger
from logging import getLogger

from wx import ClientDC

from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler

from umlshapes.lib.ogl import Shape
from umlshapes.lib.ogl import ShapeEvtHandler

from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.shapes.UmlSdInstance import UmlSdInstance

from umlshapes.types.DeltaXY import DeltaXY
from umlshapes.types.UmlPosition import NO_POSITION
from umlshapes.types.UmlPosition import UmlPosition
from umlshapes.types.UmlDimensions import UmlDimensions


class UmlSdInstanceEventHandler(UmlBaseEventHandler):

    def __init__(self, umlSdInstance: UmlSdInstance, previousEventHandler: ShapeEvtHandler, umlPubSubEngine: IUmlPubSubEngine):

        self.logger: Logger = getLogger(__name__)

        super().__init__(previousEventHandler=previousEventHandler, shape=umlSdInstance)

        self._umlPubSubEngine = umlPubSubEngine

        self._preferences: UmlPreferences = UmlPreferences()

    def OnDragLeft(self, draw, x, y, keys=0, attachment=0):
        """
        We completely override the Base Handler version

        Args:
            draw:
            x:          new x position
            y:          new y position
            keys:
            attachment:
        """

        if self._previousPosition is NO_POSITION:
            self._previousPosition = UmlPosition(x=x, y=self._preferences.instanceYPosition)
        else:
            deltaXY: DeltaXY = DeltaXY(
                deltaX=x - self._previousPosition.x,
                deltaY=y - self._previousPosition.y
            )
            # self.logger.warning(f'{deltaXY=}')
            umlShape = self.GetShape()
            umlShape.position = UmlPosition(
                x=umlShape.position.x + deltaXY.deltaX,
                y=umlShape.position.y + deltaXY.deltaY
            )

            self._previousPosition = UmlPosition(x=x, y=y)

        super().OnDragLeft(draw, x, y, keys, attachment)

    def OnDrawOutline(self, dc: ClientDC, x: int, y: int, w: int, h: int):
        """
        Called when SDInstance is moving or is resized
        We completely override the Base Handler version

        Args:
            dc: This is a client DC; It won't draw on OS X
            x: x-coordinate center of shape
            y: y-coordinate center of shape
            w: shape width
            h: shape height

        """
        from umlshapes.ShapeTypes import UmlShapeGenre

        instanceY: int = self._preferences.instanceYPosition
        self.logger.warning(f'{instanceY=} - xy: ({x},{y}) - {w=},{h=}')

        shape: Shape  = self.GetShape()
        shape.Move(dc=dc, x=x, y=instanceY, display=True)

        umlShape: UmlShapeGenre = cast(UmlShapeGenre, shape)
        umlShape.size           = UmlDimensions(width=w, height=h)
        umlShape.position       = UmlPosition(x=x, y=instanceY)

        umlShape.umlFrame.refresh()
