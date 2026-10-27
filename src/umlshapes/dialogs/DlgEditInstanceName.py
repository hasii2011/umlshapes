from wx import CANCEL
from wx import CENTER
from wx import OK

from wx import TextEntryDialog
from wx import Window


class DlgEditInstanceName(TextEntryDialog):
    """
    Syntactic sugar around a text entry dialog specifically for
    editing a sequence diagram instance's name.
    Usage:

        with DlgEditInstanceName(umlFrame, instanceName=sdInstance.instanceName) as dlg:
            if dlg.ShowModal() == ID_OK:
                sdInstance.instanceName = dlg.instanceName
    """

    def __init__(self, parent: Window, instanceName: str):
        super().__init__(parent, message='Instance Name', caption='Edit Instance Name', value=instanceName, style=OK | CANCEL | CENTER)

    @property
    def instanceName(self) -> str:
        return self.GetValue()
