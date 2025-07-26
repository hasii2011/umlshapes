
from typing import cast
from typing import List
from typing import NewType

from logging import Logger
from logging import getLogger

from wx import ClientDC
from wx import MOD_CMD

from wx.lib.ogl import Shape
from wx.lib.ogl import ShapeCanvas
from wx.lib.ogl import ShapeEvtHandler

from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine
from umlshapes.types.Common import UmlShape
from umlshapes.types.UmlDimensions import UmlDimensions

ShapeList = NewType('ShapeList', List[Shape])


class UmlBaseEventHandler(ShapeEvtHandler):

    def __init__(self, shape: Shape = None):

        self._baseLogger: Logger = getLogger(__name__)

        super().__init__(shape=shape)

        self._umlPubSubEngine: UmlPubSubEngine = cast(UmlPubSubEngine, None)

    def _setUmlPubSubEngine(self, umlPubSubEngine: UmlPubSubEngine):
        self._umlPubSubEngine = umlPubSubEngine

    # noinspection PyTypeChecker
    umlPubSubEngine = property(fget=None, fset=_setUmlPubSubEngine)

    def OnLeftClick(self, x: int, y: int, keys=0, attachment=0):

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
