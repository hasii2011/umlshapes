
from typing import cast
from typing import List
from typing import NewType
from typing import TYPE_CHECKING

from logging import INFO
from logging import Logger
from logging import getLogger

from wx import MOD_CMD
from wx import ClientDC

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
    from umlshapes.frames.UmlFrame import UmlFrame

ShapeList = NewType('ShapeList', List[Shape])


class UmlBaseEventHandler(ShapeEvtHandler):

    def __init__(self, previousEventHandler: ShapeEvtHandler, shape: Shape = None):
        from umlshapes.frames.ShapeMoveInfo import InitialPositions

        self._baseLogger: Logger = getLogger(__name__)

        super().__init__(shape=shape, prev=previousEventHandler)

        self._umlPubSubEngine:  IUmlPubSubEngine = cast(IUmlPubSubEngine, None)
        self._previousPosition: UmlPosition      = NO_POSITION

        self._initialPositions:  InitialPositions = InitialPositions({})

    def _setUmlPubSubEngine(self, umlPubSubEngine: IUmlPubSubEngine):
        self._umlPubSubEngine = umlPubSubEngine

    # noinspection PyTypeChecker
    umlPubSubEngine = property(fget=None, fset=_setUmlPubSubEngine)

    def OnDragLeft(self, draw, x, y, keys=0, attachment=0):
        """
        Move this shape, then subsequently send messages to move the other
        selected shapes (if any)

        Args:
            draw:
            x:          new x position
            y:          new y position
            keys:
            attachment:
        """
        from umlshapes.links.UmlLink import UmlLink
        from umlshapes.links.UmlLinkLabel import UmlLinkLabel

        from umlshapes.ShapeTypes import UmlShapeGenre

        from umlshapes.frames.UmlFrame import UmlFrame
        from umlshapes.frames.ShapeMoveInfo import ShapeId

        umlShape: UmlShapeGenre = cast(UmlShapeGenre, self.GetShape())
        umlFrame: UmlFrame      = self._extractFrame()
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
            self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.FRAME_MODIFIED, frameId=umlShape.umlFrame.id, modifiedFrameId=umlShape.umlFrame.id)
        else:
            if not isinstance(umlShape, UmlLinkLabel) and not isinstance(umlShape, UmlLink):

                deltaXY: DeltaXY = DeltaXY(
                    deltaX=x - self._previousPosition.x,
                    deltaY=y - self._previousPosition.y
                )
                self._previousPosition = UmlPosition(x=x, y=y)

                self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.SHAPE_MOVING, frameId=umlShape.umlFrame.id, deltaXY=deltaXY)

        super().OnDragLeft(draw, x, y, keys, attachment)

    def OnEndDragLeft(self, x, y, keys=0, attachment=0):
        """

        Args:
            x:
            y:
            keys:
            attachment:

        """
        from umlshapes.frames.UmlFrame import UmlFrame
        from umlshapes.ShapeTypes import UmlShapeGenre
        from umlshapes.commands.ShapesMovedCommand import ShapesMovedCommand

        self._previousPosition = NO_POSITION
        umlShape: UmlShapeGenre = cast(UmlShapeGenre, self.GetShape())
        self._baseLogger.info(f'{umlShape.id} - {umlShape.moveMaster}')
        umlShape.moveMaster = False

        umlFrame: UmlFrame = umlShape.umlFrame
        shapesMovedCommand: ShapesMovedCommand = ShapesMovedCommand(
            umlFrame=umlFrame,
            movedShapes=umlFrame.movedShapes,
            initialPositions=self._initialPositions
        )
        umlFrame.commandProcessor.Submit(command=shapesMovedCommand, storeIt=True)
        self._baseLogger.info(f'Pre clear {umlFrame.shapesMoving=}')

        self._debugDumpMovedShapes(umlFrame)
        umlFrame.clearMovedShapes()
        self._baseLogger.info(f'Post clear {umlFrame.shapesMoving=}')

        super().OnEndDragLeft(x, y, keys, attachment)

    def OnLeftClick(self, x: int, y: int, keys=0, attachment=0):
        """
        Keep things simple here by interacting more with OGL layer

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
        if self._umlPubSubEngine is None:
            self._baseLogger.warning(f'We do not have a pub sub engine for {shape}.  Seems like a developer error')
        else:
            self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.UML_SHAPE_SELECTED,
                                              frameId=cast(UmlFrame, canvas).id,
                                              umlShape=shape)

    def OnDrawOutline(self, dc: ClientDC, x: int, y: int, w: int, h: int):
        """
        Called when shape is moving or is resized
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

        from umlshapes.links.UmlLink import UmlLink
        from umlshapes.ShapeTypes import UmlShapeGenre
        from umlshapes.frames.UmlFrame import UmlFrame
        from umlshapes.links.UmlLinkLabel import UmlLinkLabel

        umlFrame: UmlFrame = self._extractFrame()

        shapes = umlFrame.selectedShapes
        for s in shapes:
            umlShape: UmlShapeGenre = cast(UmlShapeGenre, s)
            if not isinstance(umlShape, UmlLink) and not isinstance(umlShape, UmlLinkLabel):
                self._initialPositions[ShapeId(umlShape.id)] = umlShape.position

    def _extractFrame(self) -> 'UmlFrame':
        """
        Convenience method so I can isolate this deep coupling

        Returns:  The frame we are working on

        """
        from umlshapes.ShapeTypes import UmlShapeGenre

        umlShape: UmlShapeGenre = cast(UmlShapeGenre, self.GetShape())

        return umlShape.umlFrame

    def _debugDumpMovedShapes(self, umlFrame):
        """
        TODO: Change to DEBUG or put in a flag in the preferences

        """
        from os import linesep

        if self._baseLogger.isEnabledFor(INFO):
            self._baseLogger.info(f'----------- Start -----------')
            self._baseLogger.info(f'Pre clear {umlFrame.shapesMoving=}')
            debugLines: str = ''
            for umlId, shapeMovedInfo in umlFrame.movedShapes.items():
                debugLines = f'{debugLines}{linesep}{shapeMovedInfo=}'

            self._baseLogger.info(debugLines)
            self._baseLogger.info(f'----------- End -----------')
