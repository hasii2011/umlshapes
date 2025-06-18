
from wx import CANCEL
from wx import CENTER
from wx import OK

from wx import TextEntryDialog
from wx import Window


class DlgEditUseCase(TextEntryDialog):
    """
    Syntactic sugar around a text entry dialog specifically for
    editing a use case name
    Usage:

        with DlgEditUseCase(umlFrame, useCaseName=pyutUseCase.name) as dlg:
            if dlg.ShowModal() == ID_OK:
                pyutUseCase.name = dlg.useCaseName
    """
    def __init__(self, parent: Window, useCaseName: str):
        super().__init__(parent, message="Use Case Name", caption="Edit Use Case Name", value=useCaseName, style=OK | CANCEL | CENTER)

    @property
    def useCaseName(self) -> str:
        return self.GetValue()
