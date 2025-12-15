
from typing import Callable
from typing import cast
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from sys import maxsize

from collections.abc import Iterable

from dataclasses import dataclass

from wx import WXK_UP
from wx import EVT_CHAR
from wx import EVT_MOTION
from wx import WXK_DELETE
from wx import WXK_DOWN

from wx import ClientDC
from wx import CommandProcessor
from wx import MouseEvent
from wx import KeyEvent
from wx import Window

from umlshapes.lib.ogl import Shape
from umlshapes.lib.ogl import ShapeCanvas

from umlshapes.frames.ShapeSelector import ShapeSelector
from umlshapes.frames.DiagramFrame import DiagramFrame
from umlshapes.frames.UmlFrameOperationsListener import UmlFrameOperationsListener

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlMessageType import UmlMessageType

from umlshapes.UmlUtils import UmlUtils

from umlshapes.UmlDiagram import UmlDiagram

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.types.UmlLine import UmlLine
from umlshapes.types.UmlPosition import UmlPoint
from umlshapes.types.UmlPosition import UmlPosition
from umlshapes.types.UmlDimensions import UmlDimensions

if TYPE_CHECKING:
    from umlshapes.ShapeTypes import UmlShapes

A4_FACTOR:     float = 1.41

PIXELS_PER_UNIT_X: int = 20
PIXELS_PER_UNIT_Y: int = 20

# ModelObjects = NewType('ModelObjects', List[UmlModelBase])

BIG_NUM: int = 10000    # Hopefully, there are less than this number of shapes on frame

BOUNDARY_RIGHT_MARGIN:  int = 5
BOUNDARY_LEFT_MARGIN:   int = 5
BOUNDARY_TOP_MARGIN:    int = 5
BOUNDARY_BOTTOM_MARGIN: int = 5

@dataclass
class Ltrb:
    left:   int = 0
    top:    int = 0
    right:  int = 0
    bottom: int = 0


class UmlFrame(DiagramFrame):

    KEY_CODE_DELETE: int = WXK_DELETE
    KEY_CODE_UP:     int = WXK_UP
    KEY_CODE_DOWN:   int = WXK_DOWN

    KEY_CODE_CAPITAL_S:    int = ord('S')
    KEY_CODE_LOWER_CASE_S: int = ord('s')

    def __init__(self, parent: Window, umlPubSubEngine: IUmlPubSubEngine):

        self.ufLogger:         Logger           = getLogger(__name__)
        self._preferences:     UmlPreferences   = UmlPreferences()
        self._umlPubSubEngine: IUmlPubSubEngine = umlPubSubEngine

        super().__init__(parent=parent)

        # Doing this so key up/down Z Order code works
        self.DisableKeyboardScrolling()

        self._commandProcessor: CommandProcessor = CommandProcessor()
        self._maxWidth:  int  = self._preferences.virtualWindowWidth
        self._maxHeight: int = int(self._maxWidth / A4_FACTOR)  # 1.41 is for A4 support

        nbrUnitsX: int = self._maxWidth // PIXELS_PER_UNIT_X
        nbrUnitsY: int = self._maxHeight // PIXELS_PER_UNIT_Y
        initPosX:  int = 0
        initPosY:  int = 0
        self.SetScrollbars(PIXELS_PER_UNIT_X, PIXELS_PER_UNIT_Y, nbrUnitsX, nbrUnitsY, initPosX, initPosY, False)

        self.setInfinite(True)
        self._currentReportInterval: int = self._preferences.trackMouseInterval
        self._frameModified: bool = False

        # self._clipboard: ModelObjects = ModelObjects([])            # will be re-created at every copy

        self._umlFrameOperationsListener: UmlFrameOperationsListener = UmlFrameOperationsListener(
            umlFrame=self,
            umlPubSubEngine=self._umlPubSubEngine
        )
        # self._setupListeners()
        self.Bind(EVT_CHAR, self._onProcessKeystrokes)

    def markFrameSaved(self):
        """
        Clears the commands an ensures that CommandProcess.isDirty() is rationale
        """
        self.commandProcessor.MarkAsSaved(),
        self.commandProcessor.ClearCommands()

    @property
    def frameModified(self) -> bool:
        return self._frameModified

    @frameModified.setter
    def frameModified(self, newValue: bool):
        self._frameModified = newValue

    @property
    def commandProcessor(self) -> CommandProcessor:
        return self._commandProcessor

    @property
    def umlPubSubEngine(self) -> IUmlPubSubEngine:
        return self._umlPubSubEngine

    @property
    def umlShapes(self) -> 'UmlShapes':

        diagram: UmlDiagram = self.GetDiagram()
        return diagram.GetShapeList()

    @property
    def selectedShapes(self) -> 'UmlShapes':
        from umlshapes.ShapeTypes import UmlShapes

        selectedShapes: UmlShapes = UmlShapes([])
        umlshapes:      UmlShapes = self.umlShapes

        for shape in umlshapes:
            if shape.Selected() is True:
                selectedShapes.append(shape)

        return selectedShapes

    @property
    def shapeBoundaries(self) -> Ltrb:
        """

        Return shape boundaries as and LTRB instance

        """
        minX: int = maxsize
        maxX: int = -maxsize
        minY: int = maxsize
        maxY: int = -maxsize

        # Compute the boundaries
        for shapeInstance in self.umlDiagram.shapes:

            from umlshapes.ShapeTypes import UmlShapeGenre

            if isinstance(shapeInstance, UmlShapeGenre):
                umlShape: UmlShapeGenre = shapeInstance
                # Get shape limits
                topLeft: UmlPosition   = umlShape.position
                size:    UmlDimensions = umlShape.size

                ox1: int = topLeft.x
                oy1: int = topLeft.y
                ox2: int = size.width
                oy2: int = size.height
                ox2 += ox1
                oy2 += oy1

                # Update min-max
                minX = min(minX, ox1)
                maxX = max(maxX, ox2)
                minY = min(minY, oy1)
                maxY = max(maxY, oy2)

        # Return values
        return Ltrb(left=minX - BOUNDARY_LEFT_MARGIN,
                    top=minY - BOUNDARY_TOP_MARGIN,
                    right=maxX + BOUNDARY_RIGHT_MARGIN,
                    bottom=maxY + BOUNDARY_BOTTOM_MARGIN
                    )

    def OnLeftClick(self, x, y, keys=0):
        """
        Maybe this belongs in DiagramFrame

        Args:
            x:
            y:
            keys:
        """
        diagram: UmlDiagram = self.umlDiagram
        shapes:  Iterable = diagram.GetShapeList()

        for shape in shapes:
            umlShape: Shape     = cast(Shape, shape)
            canvas: ShapeCanvas = umlShape.GetCanvas()
            dc:     ClientDC    = ClientDC(canvas)
            canvas.PrepareDC(dc)

            umlShape.Select(select=False, dc=dc)

        self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.FRAME_LEFT_CLICK,
                                          frameId=self.id,
                                          frame=self,
                                          umlPosition=UmlPosition(x=x, y=y)
                                          )
        self.refresh()

    def OnMouseEvent(self, mouseEvent: MouseEvent):
        """
        Debug hook
        TODO:  Update the UI via an event
        Args:
            mouseEvent:

        """
        super().OnMouseEvent(mouseEvent)

        if self._preferences.trackMouse is True:
            if self._currentReportInterval == 0:
                x, y = self.CalcUnscrolledPosition(mouseEvent.GetPosition())
                self.ufLogger.info(f'({x},{y})')
                self._currentReportInterval = self._preferences.trackMouseInterval
            else:
                self._currentReportInterval -= 1

    def OnDragLeft(self, draw, x, y, keys=0):
        self.ufLogger.debug(f'{draw=} - x,y=({x},{y}) - {keys=}')

        if self._selector is None:
            self._beginSelect(x=x, y=y)

    def OnEndDragLeft(self, x, y, keys=0):

        from umlshapes.links.UmlLink import UmlLink

        self.Unbind(EVT_MOTION, handler=self._onSelectorMove)
        self.umlDiagram.RemoveShape(self._selector)

        for s in self.umlDiagram.shapes:
            if self._ignoreShape(shapeToCheck=s) is False:
                if isinstance(s, UmlLink):
                    umlLink: UmlLink = s
                    x1, y1, x2, y2 = umlLink.GetEnds()
                    umlLine: UmlLine = UmlLine(start=UmlPoint(x=x1, y=y1), end=UmlPoint(x=x2, y=y2))
                    if UmlUtils.isLineWhollyContainedByRectangle(boundingRectangle=self._selector.rectangle, umlLine=umlLine) is True:
                        umlLink.selected = True
                else:
                    from umlshapes.ShapeTypes import UmlShapeGenre
                    shape: UmlShapeGenre = cast(UmlShapeGenre, s)
                    if UmlUtils.isShapeInRectangle(boundingRectangle=self._selector.rectangle, shapeRectangle=shape.rectangle) is True:
                        shape.selected = True

        self.refresh()
        self._selector = cast(ShapeSelector, None)

        return True

    def _onProcessKeystrokes(self, event: KeyEvent):
        """

        Args:
            event:  The wxPython key event

        """
        c: int = event.GetKeyCode()
        match c:
            case UmlFrame.KEY_CODE_DELETE:
                #
                # Hmm.  Or I could send a message
                # self._umlFrameOperationsListener.cutShapes(selectedShapes=self.selectedShapes)
                self._umlPubSubEngine.sendMessage(UmlMessageType.CUT_SHAPES, frameId=self.id)
            case UmlFrame.KEY_CODE_UP:
                self._changeTheSelectedShapesZOrder(callback=self._moveShapeToFront)
                event.Skip(skip=True)
            case UmlFrame.KEY_CODE_DOWN:
                self._changeTheSelectedShapesZOrder(callback=self._moveShapeToBack)
                event.Skip(skip=True)
            case UmlFrame.KEY_CODE_LOWER_CASE_S:
                self._toggleSpline()
            case UmlFrame.KEY_CODE_CAPITAL_S:
                self._toggleSpline()
            case _:
                self.ufLogger.warning(f'Key code not supported: {c}')
                event.Skip(skip=True)

    def _unSelectAllShapesOnCanvas(self):

        shapes:  Iterable = self.umlDiagram.shapes

        for s in shapes:
            s.Select(True)

        self.Refresh(False)

    def _beginSelect(self, x: int, y: int):
        """
        Create a selector box and manage it.

        Args:
            x:
            y:

        Returns:
        """
        selector: ShapeSelector = ShapeSelector(width=0, height=0)     # RectangleShape(x, y, 0, 0)
        selector.position = UmlPosition(x, y)
        selector.originalPosition = selector.position

        selector.moving = True
        selector.diagramFrame = self

        diagram: UmlDiagram = self.umlDiagram
        diagram.AddShape(selector)

        selector.Show(True)

        self._selector = selector

        self.Bind(EVT_MOTION, self._onSelectorMove)

    def _onSelectorMove(self, event: MouseEvent):
        # from wx import Rect as WxRect

        if self._selector is not None:
            eventPosition: UmlPosition = self._getEventPosition(event)
            umlPosition:   UmlPosition = self._selector.position

            x: int = eventPosition.x
            y: int = eventPosition.y

            x0 = umlPosition.x
            y0 = umlPosition.y

            # self._selector.SetSize(x - x0, y - y0)
            self._selector.size = UmlDimensions(width=x - x0, height=y - y0)
            self._selector.position = self._selector.originalPosition

            self.refresh()

    def _getEventPosition(self, event: MouseEvent) -> UmlPosition:
        """
        Return the position of a click in the diagram.
        Args:
            event:   The mouse event

        Returns: The UML Position
        """
        x, y = self._convertEventCoordinates(event)
        return UmlPosition(x=x, y=y)

    def _ignoreShape(self, shapeToCheck):
        """

        Args:
            shapeToCheck:  The shape to check

        Returns: True if the shape is one of our ignore shapes
        """
        from umlshapes.shapes.UmlControlPoint import UmlControlPoint
        from umlshapes.links.UmlAssociationLabel import UmlAssociationLabel
        from umlshapes.links.UmlLollipopInterface import UmlLollipopInterface
        from umlshapes.shapes.UmlLineControlPoint import UmlLineControlPoint

        ignore: bool = False

        if (isinstance(shapeToCheck, UmlControlPoint) or
                isinstance(shapeToCheck, UmlAssociationLabel) or
                isinstance(shapeToCheck, UmlLollipopInterface) or
                isinstance(shapeToCheck, UmlLineControlPoint)):
            ignore = True

        return ignore

    def _toggleSpline(self):
        from umlshapes.ShapeTypes import UmlLinkGenre

        selectedShapes = self.selectedShapes

        for shape in selectedShapes:
            if isinstance(shape, UmlLinkGenre):
                shape.spline = (not shape.spline)
        self.refresh()

    def _changeTheSelectedShapesZOrder(self, callback: Callable):
        """
        Move the selected shape one level in the z-order

        Args:
            callback:  The input method determines which way
        """
        from umlshapes.ShapeTypes import UmlShapeGenre

        selectedShapes = self.selectedShapes

        if len(selectedShapes) > 0:
            for shape in selectedShapes:
                if isinstance(shape, UmlShapeGenre):
                    callback(shape)
        self.refresh()

    def _moveShapeToFront(self, shape: Shape):
        """
        Move the given shape to the top of the Z order

        Args:
            shape: The shape to move
        """
        shapesToMove = [shape] + shape.GetChildren()
        currentShapes = list(self.umlDiagram.shapes)

        for s in shapesToMove:
            currentShapes.remove(s)

        self.umlDiagram.shapes = currentShapes + shapesToMove

    def _moveShapeToBack(self, shape: Shape):
        """
        Move the given shape to the bottom of the Z order

        Args:
            shape: The shape to move
        """
        shapesToMove = [shape] + shape.GetChildren()
        currentShapes = list(self.umlDiagram.shapes)
        for s in shapesToMove:
            currentShapes.remove(s)

        self.umlDiagram.shapes = shapesToMove + currentShapes
