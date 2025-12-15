
from logging import Logger
from logging import getLogger

from wx import OK

from umlmodel.Interface import Interfaces

from umlshapes.dialogs.DlgEditInterface import DlgEditInterface

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame

from umlshapes.links.UmlLollipopInterface import UmlLollipopInterface

from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler


class UmlLollipopInterfaceEventHandler(UmlBaseEventHandler):
    """
    Exists to popup the edit dialog
    """

    def __init__(self, lollipopInterface: UmlLollipopInterface):

        self.logger: Logger = getLogger(__name__)
        super().__init__(shape=lollipopInterface, previousEventHandler=lollipopInterface.GetEventHandler())

        lollipopInterface.SetEventHandler(self)

    def OnLeftDoubleClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):

        super().OnLeftDoubleClick(x=x, y=y, keys=keys, attachment=attachment)

        umlLollipopInterface: UmlLollipopInterface = self.GetShape()
        umlFrame:             ClassDiagramFrame     = umlLollipopInterface.GetCanvas()
        umlLollipopInterface.selected = False
        umlFrame.refresh()

        self.logger.info(f'{umlLollipopInterface=}')

        eventEngine: IUmlPubSubEngine = umlFrame.umlPubSubEngine
        interfaces:  Interfaces  = umlFrame.getDefinedInterfaces()

        with DlgEditInterface(parent=umlFrame, lollipopInterface=umlLollipopInterface, umlPubSubEngine=eventEngine, interfaces=interfaces, editMode=True) as dlg:
            if dlg.ShowModal() == OK:
                umlFrame.refresh()
