
from typing import cast
from typing import List
from typing import NewType

from logging import Logger
from logging import getLogger

from wx import ClientDC
from wx import MOD_CMD

from umlshapes.lib.ogl import Shape
from umlshapes.lib.ogl import ShapeCanvas
from umlshapes.lib.ogl import ShapeEvtHandler

from umlshapes.pubsubengine.UmlMessageType import UmlMessageType
from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine

from umlshapes.types.Common import UmlShape
from umlshapes.types.DeltaXY import DeltaXY
from umlshapes.types.UmlPosition import UmlPosition
from umlshapes.types.UmlDimensions import UmlDimensions

ShapeList = NewType('ShapeList', List[Shape])

NO_POSITION = cast(UmlPosition, None)


class UmlBaseEventHandler(ShapeEvtHandler):

    def __init__(self, shape: Shape = None):

        self._baseLogger: Logger = getLogger(__name__)

        super().__init__(shape=shape)

        self._umlPubSubEngine:  UmlPubSubEngine = cast(UmlPubSubEngine, None)
        self._previousPosition: UmlPosition     = NO_POSITION

    def _setUmlPubSubEngine(self, umlPubSubEngine: UmlPubSubEngine):
        self._umlPubSubEngine = umlPubSubEngine

    # noinspection PyTypeChecker
    umlPubSubEngine = property(fget=None, fset=_setUmlPubSubEngine)

    def OnDragLeft(self, draw, x, y, keys = 0, attachment = 0):
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

        from umlshapes.links.UmlAssociationLabel import UmlAssociationLabel
        from umlshapes.links.UmlLink import UmlLink
        # self._baseLogger.info(f'{draw=} x,y:({x},{y}) {attachment=}')
        umlShape: UmlShape = cast(UmlShape, self.GetShape())

        if self._previousPosition is NO_POSITION:
            self._previousPosition = UmlPosition(x=x, y=y)
            umlShape.moveMaster = True
            self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.FRAME_MODIFIED, frameId=umlShape.umlFrame.id, modifiedFrameId=umlShape.umlFrame.id)
        else:
            if not isinstance(umlShape, UmlAssociationLabel) and not isinstance(umlShape, UmlLink):

                deltaXY: DeltaXY = DeltaXY(
                    deltaX=x - self._previousPosition.x,
                    deltaY=y - self._previousPosition.y
                )
                self._previousPosition = UmlPosition(x=x, y=y)

                self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.SHAPE_MOVING, frameId=umlShape.umlFrame.id, deltaXY=deltaXY)

        super().OnDragLeft(draw, x, y, keys, attachment)

    def OnEndDragLeft(self, x, y, keys=0, attachment=0):

        # self._baseLogger.info(f'x,y:({x},{y}) {keys=} {attachment=}')
        self._previousPosition = NO_POSITION
        umlShape: UmlShape = cast(UmlShape, self.GetShape())
        umlShape.moveMaster = False

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
                                              frameId=cast(UmlFrame,canvas).id,
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
        shape: Shape  = self.GetShape()
        shape.Move(dc=dc, x=x, y=y, display=True)

        umlShape: UmlShape = cast(UmlShape, shape)
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
