
from wx import CANCEL
from wx import CENTER
from wx import OK

from wx import TextEntryDialog
from wx import Window


class DlgEditActor(TextEntryDialog):
    """
    Syntactic sugar around a text entry dialog specifically for
    editing an actor's name
    Usage:

        with DlgEditActor(umlFrame, useCaseName=pyutActor.name) as dlg:
            if dlg.ShowModal() == ID_OK:
                pyutActor.name = dlg.actorName
    """
    def __init__(self, parent: Window, actorName: str):
        super().__init__(parent, message="Actor Name", caption="Edit Actor Name", value=actorName, style=OK | CANCEL | CENTER)

    @property
    def actorName(self) -> str:
        return self.GetValue()
