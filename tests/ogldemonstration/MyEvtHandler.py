
from logging import Logger
from logging import getLogger

from wx import ClientDC
from wx import PlatformInfo

from umlshapes.lib.ogl import ShapeEvtHandler


class MyEvtHandler(ShapeEvtHandler):
    def __init__(self, frame):

        # ShapeEvtHandler.__init__(self)

        super().__init__(self)
        self.logger: Logger = getLogger(__name__)
        self.statusBarFrame = frame

    def UpdateStatusBar(self, shape):
        x, y = shape.GetX(), shape.GetY()
        width, height = shape.GetBoundingBoxMax()
        self.statusBarFrame.SetStatusText("Pos: (%d, %d)  Size: (%d, %d)" %
                                          (x, y, width, height))

    def OnLeftClick(self, x, y, keys=0, attachment=0):
        shape = self.GetShape()
        canvas = shape.GetCanvas()
        dc = ClientDC(canvas)
        canvas.PrepareDC(dc)

        if shape.Selected():
            shape.Select(False, dc)
            # canvas.Redraw(dc)
            canvas.Refresh(False)
        else:
            # redraw = False
            shapeList = canvas.GetDiagram().GetShapeList()
            toUnselect = []

            for s in shapeList:
                if s.Selected():
                    # If we unselect it now then some of the objects in
                    # shapeList will become invalid (the control points are
                    # shapes too!) and bad things will happen...
                    toUnselect.append(s)

            shape.Select(True, dc)

            if toUnselect:
                for s in toUnselect:
                    s.Select(False, dc)

                # #canvas.Redraw(dc)
                canvas.Refresh(False)

        self.UpdateStatusBar(shape)

    def OnEndDragLeft(self, x, y, keys=0, attachment=0):
        shape = self.GetShape()
        ShapeEvtHandler.OnEndDragLeft(self, x, y, keys, attachment)

        if not shape.Selected():
            self.OnLeftClick(x, y, keys, attachment)

        self.UpdateStatusBar(shape)

    def OnSizingEndDragLeft(self, pt, x, y, keys=0, attachment=0):
        # ogl.ShapeEvtHandler.OnSizingEndDragLeft(self, pt, draw, x, y, keys, attachment)
        super().OnSizingEndDragLeft(pt=pt, x=x, y=y, keys=keys, attachment=attachment)
        self.UpdateStatusBar(self.GetShape())

    def OnMovePost(self, dc, x, y, oldX, oldY, display=0):

        shape = self.GetShape()
        # ogl.ShapeEvtHandler.OnMovePost(self, dc, x, y, oldX, oldY, display)
        super().OnMovePost(dc, x, y, oldX, oldY, display=True)

        self.UpdateStatusBar(shape)
        if "wxMac" in PlatformInfo:
            shape.GetCanvas().Refresh(False)

    def OnRightClick(self, *doNotCare):
        self.logger.info(f'{self.GetShape()}')
