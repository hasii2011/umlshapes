
from logging import Logger
from logging import getLogger

from wx import ClientDC

from umlshapes.lib.ogl import ShapeEvtHandler

from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine


class UmlSdInstanceEventHandler(ShapeEvtHandler):

    def __init__(self, umlPubSubEngine: IUmlPubSubEngine):

        self.logger: Logger = getLogger(__name__)

        # super().__init__(previousEventHandler=previousEventHandler, shape=umlSdInstance)
        super().__init__()
        self._umlPubSubEngine = umlPubSubEngine

        self._preferences: UmlPreferences = UmlPreferences()

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

    def OnEndDragLeft(self, x, y, keys=0, attachment=0):
        shape = self.GetShape()
        ShapeEvtHandler.OnEndDragLeft(self, x, y, keys, attachment)

        if not shape.Selected():
            self.OnLeftClick(x, y, keys, attachment)

    def OnSizingEndDragLeft(self, pt, x, y, keys=0, attachment=0):
        super().OnSizingEndDragLeft(pt=pt, x=x, y=y, keys=keys, attachment=attachment)

    def OnMovePost(self, dc, x, y, oldX, oldY, display=0):

        shape = self.GetShape()
        super().OnMovePost(dc, x, y, oldX, oldY, display=True)

        shape.GetCanvas().Refresh(False)
