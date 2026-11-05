
from typing import cast
from typing import List
from typing import NewType
from typing import Optional
from typing import TYPE_CHECKING

from logging import DEBUG
from logging import Logger
from logging import getLogger

from wx import MOD_CMD
from wx import ClientDC
from wx import Window

from umlshapes.lib.ogl import Shape
from umlshapes.lib.ogl import ShapeCanvas
from umlshapes.lib.ogl import ShapeEvtHandler

from umlshapes.pubsubengine.UmlMessageType import UmlMessageType
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.types.DeltaXY import DeltaXY
from umlshapes.types.UmlPosition import UmlPosition
from umlshapes.types.UmlPosition import NO_POSITION
from umlshapes.types.UmlDimensions import UmlDimensions


if TYPE_CHECKING:
    from umlshapes.ShapeTypes import UmlShapeGenre
    from umlshapes.frames.UmlFrame import UmlFrame

ShapeList = NewType('ShapeList', List[Shape])


class UmlBaseEventHandler(ShapeEvtHandler):

    def __init__(self, previousEventHandler: ShapeEvtHandler, shape: Optional[Shape] = None):
        """

        Args:
            previousEventHandler:
            shape:
        """
        from umlshapes.frames.ShapeMoveInfo import InitialPositions

        self._baseLogger: Logger = getLogger(__name__)

        super().__init__(shape=shape, prev=previousEventHandler)

        self._umlPubSubEngine:  Optional[IUmlPubSubEngine] = None
        self._previousPosition: UmlPosition                = NO_POSITION

        self._initialPositions:  InitialPositions = InitialPositions({})

    @property
    def umlPubSubEngine(self) -> IUmlPubSubEngine:
        assert self._umlPubSubEngine is not None, 'Developer error: pub sub engine not set'
        return self._umlPubSubEngine

    @umlPubSubEngine.setter
    def umlPubSubEngine(self, umlPubSubEngine: IUmlPubSubEngine):
        self._umlPubSubEngine = umlPubSubEngine

    def OnLeftDoubleClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Overrides ShapeEvtHandler.OnLeftDoubleClick to ensure any active mouse
        capture on the diagram canvas or frame is released before double-click
        handling proceeds.

        Args:
            x:          Cursor X coordinate
            y:          Cursor Y coordinate
            keys:       Modifier keys mask
            attachment: Attachment point index
        """
        super().OnLeftDoubleClick(x=x, y=y, keys=keys, attachment=attachment)

        shape: Optional[Shape] = self.GetShape()
        if shape is not None:
            canvas: Optional[ShapeCanvas] = shape.GetCanvas()
            if canvas is not None:
                if canvas.HasCapture():
                    canvas.ReleaseMouse()
            else:
                umlFrame: Optional[Window] = getattr(shape, 'umlFrame', None)
                if umlFrame is not None:
                    if umlFrame.HasCapture():
                        umlFrame.ReleaseMouse()

    def OnBeginDragLeft(self, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Overrides ShapeEvtHandler.OnBeginDragLeft to record the initial position
        of the dragged shape and any other selected shapes before movement starts.

        Args:
            x:          initial x position
            y:          initial y position
            keys:
            attachment:
        """
        from umlshapes.mixins.TopLeftMixin import TopLeftMixin
        from umlshapes.shapes.UmlBaseLabel import UmlBaseLabel

        from umlshapes.ShapeTypes import UmlShapeGenre

        from umlshapes.frames.UmlFrame import UmlFrame

        umlShape: UmlShapeGenre = cast(UmlShapeGenre, self.GetShape())
        umlFrame: UmlFrame      = self._extractFrame()

        if isinstance(umlShape, TopLeftMixin) and not isinstance(umlShape, UmlBaseLabel):
            self._handleTopLeftShapeDrag(umlShape=umlShape, umlFrame=umlFrame, x=x, y=y)

        super().OnBeginDragLeft(x, y, keys, attachment)

    def OnDragLeft(self, draw, x, y, keys=0, attachment=0):
        """
        Overrides ShapeEvtHandler.OnDragLeft to move this shape, then subsequently
        send messages to move the other selected shapes (if any).

        Args:
            draw:
            x:          new x position
            y:          new y position
            keys:
            attachment:
        """
        from umlshapes.mixins.TopLeftMixin import TopLeftMixin
        from umlshapes.shapes.UmlBaseLabel import UmlBaseLabel

        from umlshapes.ShapeTypes import UmlShapeGenre

        from umlshapes.frames.UmlFrame import UmlFrame

        umlShape: UmlShapeGenre = cast(UmlShapeGenre, self.GetShape())
        umlFrame: UmlFrame      = self._extractFrame()

        if isinstance(umlShape, TopLeftMixin) and not isinstance(umlShape, UmlBaseLabel):
            self._handleTopLeftShapeDrag(umlShape=umlShape, umlFrame=umlFrame, x=x, y=y)

        super().OnDragLeft(draw, x, y, keys, attachment)

    def OnEndDragLeft(self, x, y, keys=0, attachment=0):
        """
        Overrides ShapeEvtHandler.OnEndDragLeft to finalize the drag operation
        and submit a ShapesMovedCommand.

        Args:
            x:
            y:
            keys:
            attachment:

        """
        from umlshapes.frames.UmlFrame import UmlFrame
        from umlshapes.frames.ShapeMoveInfo import InitialPositions

        from umlshapes.ShapeTypes import UmlShapeGenre
        from umlshapes.commands.ShapesMovedCommand import ShapesMovedCommand

        self._previousPosition = NO_POSITION
        umlShape: UmlShapeGenre = cast(UmlShapeGenre, self.GetShape())
        self._baseLogger.debug(f'{umlShape.id} - {umlShape.moveMaster}')
        umlShape.moveMaster = False

        umlFrame: UmlFrame = umlShape.umlFrame
        shapesMovedCommand: ShapesMovedCommand = ShapesMovedCommand(
            umlFrame=umlFrame,
            movedShapes=umlFrame.movedShapes,
            initialPositions=self._initialPositions
        )
        umlFrame.commandProcessor.Submit(command=shapesMovedCommand, storeIt=True)
        self._baseLogger.debug(f'Pre clear {umlFrame.shapesMoving=}')

        self._debugDumpMovedShapes(umlFrame)
        umlFrame.clearMovedShapes()
        self._initialPositions = InitialPositions({})

        self._baseLogger.debug(f'Post clear {umlFrame.shapesMoving=}')

        super().OnEndDragLeft(x, y, keys, attachment)

    def OnLeftClick(self, x: int, y: int, keys=0, attachment=0):
        """
        Overrides ShapeEvtHandler.OnLeftClick. Keep things simple here by
        interacting more with OGL layer.

        Args:
            x:
            y:
            keys:
            attachment:

        Returns:

        """
        from umlshapes.frames.UmlFrame import UmlFrame

        self._baseLogger.debug(f'({x},{y}), {keys=} {attachment=}')
        shape:  Shape       = self.GetShape()
        canvas: ShapeCanvas = shape.GetCanvas()
        dc:     ClientDC    = ClientDC(canvas)

        canvas.PrepareDC(dc)

        if keys == MOD_CMD:
            pass
        else:
            self._unSelectAllShapesOnCanvas(shape, canvas, dc)

        shape.Select(True, dc)
        self.umlPubSubEngine.sendMessage(messageType=UmlMessageType.UML_SHAPE_SELECTED,
                                         frameId=cast(UmlFrame, canvas).id,
                                         umlShape=shape)

        cast(UmlFrame, canvas).refresh()

    def OnDrawOutline(self, dc: ClientDC, x: int, y: int, w: int, h: int):
        """
        Overrides ShapeEvtHandler.OnDrawOutline. Called when shape is moving
        or is resized.

        Args:
            dc:  This is a client DC; It won't draw on OS X
            x:
            y:
            w:
            h:
        """
        from umlshapes.ShapeTypes import UmlShapeGenre

        shape: Shape  = self.GetShape()
        shape.Move(dc=dc, x=x, y=y, display=True)

        umlShape: UmlShapeGenre = cast(UmlShapeGenre, shape)
        umlShape.size = UmlDimensions(width=w, height=h)
        umlShape.umlFrame.refresh()

    def _handleTopLeftShapeDrag(self, umlShape: 'UmlShapeGenre', umlFrame: 'UmlFrame', x: int, y: int):
        """
        Track initial positions on the first drag event and publish movement deltas
        on subsequent drag events for shapes that inherit from TopLeftMixin.

        Args:
            umlShape: The dragged shape acting as move master
            umlFrame: The diagram frame containing the shape
            x:        New cursor X coordinate
            y:        New cursor Y coordinate
        """
        from umlshapes.frames.ShapeMoveInfo import ShapeId

        #
        # Only the move master moves himself
        # The first time through we have no way of calculating the delta
        # The other selected shapes get moved by the frame operations listener (indirectly)
        #
        if self._previousPosition is NO_POSITION:
            self._previousPosition = UmlPosition(x=x, y=y)
            umlShape.moveMaster = True
            self._saveSelectedShapesInitialPositions()

            umlFrame.markShapeAsMoved(umlShape=umlShape)
            #
            # Save the master shape position, in case he is not selected
            #
            self._initialPositions[ShapeId(umlShape.id)] = umlShape.position

            self._baseLogger.info(f'Initial Position Count: {len(self._initialPositions)}')

            self.umlPubSubEngine.sendMessage(messageType=UmlMessageType.FRAME_MODIFIED, frameId=umlShape.umlFrame.id, modifiedFrameId=umlShape.umlFrame.id)
        else:

            deltaXY: DeltaXY = DeltaXY(
                deltaX=x - self._previousPosition.x,
                deltaY=y - self._previousPosition.y
            )
            self._previousPosition = UmlPosition(x=x, y=y)

            self.umlPubSubEngine.sendMessage(messageType=UmlMessageType.SHAPE_MOVING, frameId=umlShape.umlFrame.id, deltaXY=deltaXY)

    def _unSelectAllShapesOnCanvas(self, shape: Shape, canvas: ShapeCanvas, dc: ClientDC):

        # Unselect if already selected
        if shape.Selected() is True:
            shape.Select(False, dc)
            canvas.Refresh(False)
        else:
            shapeList: ShapeList = canvas.GetDiagram().GetShapeList()
            toUnselect: ShapeList = ShapeList([])

            for s in shapeList:
                if s.Selected() is True:
                    # If we unselect it, then some objects in
                    # shapeList will become invalid (the control points are
                    # shapes too!) and bad things will happen...
                    toUnselect.append(s)

            if len(toUnselect) > 0:
                for s in toUnselect:
                    s.Select(False, dc)

                canvas.Refresh(False)

    def _saveSelectedShapesInitialPositions(self):
        """
        Save initial positions of selected shapes so when the drag ends we can
        inject them into the `ShapesMovedCommand`
        """
        from umlshapes.frames.ShapeMoveInfo import ShapeId

        from umlshapes.mixins.TopLeftMixin import TopLeftMixin
        from umlshapes.ShapeTypes import UmlShapeGenre
        from umlshapes.frames.UmlFrame import UmlFrame
        from umlshapes.shapes.UmlBaseLabel import UmlBaseLabel

        umlFrame: UmlFrame = self._extractFrame()

        shapes = umlFrame.selectedShapes
        from umlshapes.sd.UmlSDMessage import UmlSDMessage
        for s in shapes:
            if isinstance(s, UmlSDMessage):
                self._initialPositions[ShapeId(s.id)] = s.position
            else:
                umlShape: UmlShapeGenre = cast(UmlShapeGenre, s)
                if isinstance(umlShape, TopLeftMixin) and not isinstance(umlShape, UmlBaseLabel):
                    self._initialPositions[ShapeId(umlShape.id)] = umlShape.position

    def _extractFrame(self) -> 'UmlFrame':
        """
        Convenience method so I can isolate this deep coupling

        Returns:  The frame we are working on

        """
        from umlshapes.ShapeTypes import UmlShapeGenre

        umlShape: UmlShapeGenre = cast(UmlShapeGenre, self.GetShape())

        return umlShape.umlFrame

    def _indicateFrameModified(self):

        frame: UmlFrame = self._getFrame()

        self.umlPubSubEngine.sendMessage(UmlMessageType.FRAME_MODIFIED, frameId=frame.id, modifiedFrameId=frame.id)

    def _getFrame(self) -> 'UmlFrame':

        shape:    Shape      = self.GetShape()
        umlFrame: 'UmlFrame' = shape.GetCanvas()

        return umlFrame

    def _debugDumpMovedShapes(self, umlFrame):
        """
        TODO: Change to DEBUG or put in a flag in the preferences

        """
        from os import linesep

        if self._baseLogger.isEnabledFor(DEBUG):
            self._baseLogger.debug(f'----------- Start -----------')
            self._baseLogger.debug(f'Pre clear {umlFrame.shapesMoving=}')
            debugLines: str = ''
            for umlId, shapeMovedInfo in umlFrame.movedShapes.items():
                debugLines = f'{debugLines}{linesep}{shapeMovedInfo=}'

            self._baseLogger.debug(debugLines)
            self._baseLogger.debug(f'----------- End -----------')
