
from logging import Logger
from logging import getLogger

from wx import ID_OK

from umlmodel.UseCase import UseCase

from umlshapes.lib.ogl import ShapeEvtHandler

from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler

from umlshapes.dialogs.DlgEditUseCase import DlgEditUseCase

from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.shapes.UmlUseCase import UmlUseCase


class UmlUseCaseEventHandler(UmlBaseEventHandler):
    """
    Nothing special here;  Just some syntactic sugar
    """

    def __init__(self, previousEventHandler: ShapeEvtHandler):
        self.logger: Logger = getLogger(__name__)

        super().__init__(previousEventHandler=previousEventHandler)

    def OnLeftDoubleClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):

        super().OnLeftDoubleClick(x=x, y=y, keys=keys, attachment=attachment)

        umlUseCase:   UmlUseCase = self.GetShape()
        modelUseCase: UseCase    = umlUseCase.modelUseCase

        umlFrame:  UmlFrame  = umlUseCase.GetCanvas()

        with DlgEditUseCase(umlFrame, useCaseName=modelUseCase.name) as dlg:
            if dlg.ShowModal() == ID_OK:
                modelUseCase.name = dlg.useCaseName
                umlFrame.refresh()
