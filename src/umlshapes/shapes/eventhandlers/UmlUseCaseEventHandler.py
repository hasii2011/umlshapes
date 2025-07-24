
from logging import Logger
from logging import getLogger

from wx import ID_OK

from pyutmodelv2.PyutUseCase import PyutUseCase

from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler
from umlshapes.dialogs.DlgEditUseCase import DlgEditUseCase
from umlshapes.frames.UmlFrame import UmlFrame
from umlshapes.shapes.UmlUseCase import UmlUseCase


class UmlUseCaseEventHandler(UmlBaseEventHandler):
    """
    Nothing special here;  Just some syntactic sugar
    """

    def __init__(self):
        self.logger: Logger = getLogger(__name__)

        super().__init__()

    def OnLeftDoubleClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):

        super().OnLeftDoubleClick(x=x, y=y, keys=keys, attachment=attachment)

        umlUseCase:  UmlUseCase  = self.GetShape()
        pyutUseCase: PyutUseCase = umlUseCase.pyutUseCase

        umlFrame:  UmlFrame  = umlUseCase.GetCanvas()

        with DlgEditUseCase(umlFrame, useCaseName=pyutUseCase.name) as dlg:
            if dlg.ShowModal() == ID_OK:
                pyutUseCase.name = dlg.useCaseName
                umlFrame.refresh()
