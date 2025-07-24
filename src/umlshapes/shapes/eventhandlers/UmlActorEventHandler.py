
from logging import Logger
from logging import getLogger

from wx import ID_OK

from pyutmodelv2.PyutActor import PyutActor

from umlshapes.dialogs.DlgEditActor import DlgEditActor
from umlshapes.frames.UmlFrame import UmlFrame
from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler
from umlshapes.shapes.UmlActor import UmlActor


class UmlActorEventHandler(UmlBaseEventHandler):
    """
    Nothing special here;  Just some syntactic sugar
    """

    def __init__(self):
        self.logger:       Logger         = getLogger(__name__)
        self._preferences: UmlPreferences = UmlPreferences()
        super().__init__()

    def OnLeftDoubleClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):

        super().OnLeftDoubleClick(x=x, y=y, keys=keys, attachment=attachment)

        umlActor:  UmlActor  = self.GetShape()
        pyutActor: PyutActor = umlActor.pyutActor

        umlFrame:  UmlFrame  = umlActor.GetCanvas()

        with DlgEditActor(parent=umlFrame, actorName=pyutActor.name,) as dlg:
            if dlg.ShowModal() == ID_OK:
                pyutActor.name = dlg.actorName
                umlFrame.refresh()

        umlActor.selected = False
