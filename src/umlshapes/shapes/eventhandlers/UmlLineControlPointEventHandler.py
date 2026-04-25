
from typing import cast

from logging import Logger
from logging import getLogger

from wx import CURSOR_DEFAULT

from wx import Cursor

from umlshapes.lib.ogl import ShapeEvtHandler

from umlshapes.UmlUtils import UmlUtils
from umlshapes.utils.ProximityUtils import ProximityUtils

from umlshapes.frames.DiagramFrame import DiagramFrame
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlMessageType import UmlMessageType

from umlshapes.shapes.UmlLineControlPoint import UmlLineControlPoint
from umlshapes.shapes.UmlLineControlPoint import UmlLineControlPointType

from umlshapes.types.Common import EndPositions
from umlshapes.types.Common import Rectangle

from umlshapes.types.UmlPosition import UmlPosition


class UmlLineControlPointEventHandler(ShapeEvtHandler):
    """
    Add in the following custom behavior
        * Don't use the funky cursor
        * Indicate a change was made on the diagram
        * Move the end control points
    """
    def __init__(self):
        self.logger: Logger = getLogger(__name__)

        self._umlPubSubEngine:  IUmlPubSubEngine = cast(IUmlPubSubEngine, None)

        super().__init__()

    def _setUmlPubSubEngine(self, umlPubSubEngine: IUmlPubSubEngine):
        self._umlPubSubEngine = umlPubSubEngine

    # noinspection PyTypeChecker
    umlPubSubEngine = property(fget=None, fset=_setUmlPubSubEngine)

    def OnDragLeft(self, draw: bool, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        The drag left handler.  This appears to be the only event handler
        invoked regardless of which direction you are dragging

        We are using this handler to move the line end points

        Args:
            draw:
            x:
            y:
            keys:
            attachment:
        """

        umlLineControlPoint:     UmlLineControlPoint     = self.GetShape()
        umlLineControlPointType: UmlLineControlPointType = umlLineControlPoint.umlLineControlPointType

        if self._isThisAnEndLineControlPoint(umlLineControlPointType=umlLineControlPointType) is True:
            from umlshapes.links.UmlLink import UmlLink

            # Override OGL
            defaultCursor: Cursor = Cursor(CURSOR_DEFAULT)
            umlLineControlPoint.GetCanvas().SetCursor(defaultCursor)

            umlLink: UmlLink = umlLineControlPoint.attachedTo
            self.logger.debug(f'{umlLineControlPoint=} x,y: ({x},{y})')

            if umlLineControlPointType == UmlLineControlPointType.FROM_ENDPOINT:
                self._moveTheFromPoint(umlLineControlPoint, umlLink, x, y)
            elif umlLineControlPointType == UmlLineControlPointType.TO_ENDPOINT:
                self._moveTheToPoint(umlLineControlPoint, umlLink, x, y)

        else:
            super().OnDragLeft(draw, x, y, keys, attachment)

        diagramFrame: DiagramFrame = umlLineControlPoint.GetCanvas()
        diagramFrame.refresh()
        self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.FRAME_MODIFIED, frameId=diagramFrame.id, modifiedFrameId=diagramFrame.id)

    def _moveTheToPoint(self, umlLineControlPoint, umlLink, x, y):
        """

        Args:
            umlLineControlPoint:
            umlLink:
            x:
            y:

        """
        from umlshapes.shapes.UmlClass import UmlClass

        umlClass:       UmlClass    = umlLink.GetTo()
        rectangle:      Rectangle   = umlClass.rectangle
        borderPosition: UmlPosition = ProximityUtils.getNearestPointOnRectangle(x=x, y=y, rectangle=rectangle)

        self.logger.debug(f'{umlLink=} {umlClass=} {borderPosition=}')

        endPoints: EndPositions = umlLink.endPositions
        newTo:     EndPositions = EndPositions(
            fromPosition=endPoints.fromPosition,
            toPosition=borderPosition
        )
        umlLink.endPositions         = newTo
        umlLineControlPoint.position = borderPosition

    def _moveTheFromPoint(self, umlLineControlPoint, umlLink, x, y):
        """

        Args:
            umlLineControlPoint:
            umlLink:
            x:
            y:
        """
        from umlshapes.shapes.UmlClass import UmlClass

        umlClass:       UmlClass    = umlLink.GetFrom()
        rectangle:      Rectangle   = umlClass.rectangle
        borderPosition: UmlPosition = ProximityUtils.getNearestPointOnRectangle(x=x, y=y, rectangle=rectangle)

        self.logger.debug(f'{umlLink=} {umlClass=} {borderPosition=}')

        endPoints: EndPositions = umlLink.endPositions
        newFrom:   EndPositions = EndPositions(
            fromPosition=borderPosition,
            toPosition=endPoints.toPosition
        )
        #
        # Move the line and the control point
        #
        umlLink.endPositions         = newFrom
        umlLineControlPoint.position = borderPosition

    def _isThisAnEndLineControlPoint(self, umlLineControlPointType: UmlLineControlPointType) -> bool:
        """
        Boolean syntactical sugar
        Args:
            umlLineControlPointType:

        Returns:  'True' if it is, else 'False'
        """

        ans: bool = False
        if umlLineControlPointType == UmlLineControlPointType.FROM_ENDPOINT or umlLineControlPointType == UmlLineControlPointType.TO_ENDPOINT:
            ans = True

        return ans
