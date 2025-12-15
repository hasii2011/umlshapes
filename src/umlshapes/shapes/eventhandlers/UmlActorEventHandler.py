
from logging import Logger
from logging import getLogger

from wx import ID_OK

from umlmodel.Actor import Actor

from umlshapes.lib.ogl import ShapeEvtHandler

from umlshapes.dialogs.DlgEditActor import DlgEditActor
from umlshapes.frames.UmlFrame import UmlFrame
from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler
from umlshapes.shapes.UmlActor import UmlActor


class UmlActorEventHandler(UmlBaseEventHandler):
    """
    Nothing special here;  Just some syntactic sugar
    """

    def __init__(self, previousEventHandler: ShapeEvtHandler):
        self.logger:       Logger         = getLogger(__name__)
        self._preferences: UmlPreferences = UmlPreferences()
        super().__init__(previousEventHandler=previousEventHandler)

    def OnLeftDoubleClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):

        super().OnLeftDoubleClick(x=x, y=y, keys=keys, attachment=attachment)

        umlActor:   UmlActor = self.GetShape()
        modelActor: Actor    = umlActor.modelActor

        umlFrame:  UmlFrame  = umlActor.GetCanvas()

        with DlgEditActor(parent=umlFrame, actorName=modelActor.name,) as dlg:
            if dlg.ShowModal() == ID_OK:
                modelActor.name = dlg.actorName
                umlFrame.refresh()

        umlActor.selected = False
