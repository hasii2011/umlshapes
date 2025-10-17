
from logging import Logger
from logging import getLogger

from wx import OK

from pyutmodelv2.PyutInterface import PyutInterfaces

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
        super().__init__(shape=lollipopInterface)

    def OnLeftDoubleClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):

        super().OnLeftDoubleClick(x=x, y=y, keys=keys, attachment=attachment)

        umlLollipopInterface: UmlLollipopInterface = self.GetShape()
        umlFrame:             ClassDiagramFrame     = umlLollipopInterface.GetCanvas()
        umlLollipopInterface.selected = False
        umlFrame.refresh()

        self.logger.info(f'{umlLollipopInterface=}')

        eventEngine:    IUmlPubSubEngine = umlFrame.umlPubSubEngine
        pyutInterfaces: PyutInterfaces  = umlFrame.getDefinedInterfaces()

        with DlgEditInterface(parent=umlFrame, lollipopInterface=umlLollipopInterface, umlPubSubEngine=eventEngine, pyutInterfaces=pyutInterfaces, editMode=True) as dlg:
            if dlg.ShowModal() == OK:
                umlFrame.refresh()
