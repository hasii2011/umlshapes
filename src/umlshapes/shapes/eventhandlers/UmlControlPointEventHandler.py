
from logging import Logger
from logging import getLogger

from wx.lib.ogl import Shape
from wx.lib.ogl import ShapeEvtHandler

from umlshapes.DiagramFrame import DiagramFrame


class UmlControlPointEventHandler(ShapeEvtHandler):

    def __init__(self):
        self.logger: Logger = getLogger(__name__)

        super().__init__()

    def OnDragLeft(self, draw: bool, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        The drag left handler.  This appears to be the only event handler
        invoked regardless of which direction you are dragging

        Args:
            draw:
            x:
            y:
            keys:
            attachment:
        """
        from umlshapes.shapes.UmlText import UmlText

        shape:   Shape        = self.GetShape()
        umlText: UmlText      = shape.GetParent()
        canvas:  DiagramFrame = umlText.GetCanvas()

        canvas.refresh()
        super().OnDragLeft(draw, x, y, keys, attachment)

    def OnBeginDragLeft(self, x, y, keys=0, attachment=0):
        """
        The drag left started handler.
        """
        self.logger.info(f'({x},{y})')
        super().OnBeginDragLeft(x, y, keys, attachment)

    def OnEndDragLeft(self, x, y, keys=0, attachment=0):
        """
        The drag left ended handler.
        """
        super().OnEndDragLeft(x, y, keys, attachment)

    def OnDragRight(self, draw, x, y, keys=0, attachment=0):
        """
        The drag right handler.
        """
        self.logger.info(f'({x},{y})')
        super().OnDragRight(draw, x, y, keys, attachment)

    def OnBeginDragRight(self, x, y, keys=0, attachment=0):
        """
        The drag right start handler.
        """
        self.logger.info(f'({x},{y})')
        super().OnBeginDragRight(x, y, keys, attachment)

    def OnEndDragRight(self, x, y, keys=0, attachment=0):
        """
        The drag right ended handler.
        """
        self.logger.info(f'({x},{y})')
        super().OnEndDragRight(x, y, keys, attachment)
