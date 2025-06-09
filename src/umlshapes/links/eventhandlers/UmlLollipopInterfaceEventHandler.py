
from logging import Logger
from logging import getLogger

from wx import OK

from umlshapes.dialogs.DlgEditInterface import DlgEditInterface
from umlshapes.frames.UmlClassDiagramFrame import UmlClassDiagramFrame

from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler

from pyutmodelv2.PyutInterface import PyutInterface
from pyutmodelv2.PyutInterface import PyutInterfaces

from umlshapes.links.UmlLollipopInterface import UmlLollipopInterface
from umlshapes.types.Common import UmlShapeList


class UmlLollipopInterfaceEventHandler(UmlBaseEventHandler):

    def __init__(self, lollipopInterface: UmlLollipopInterface):

        self.logger: Logger = getLogger(__name__)
        super().__init__(shape=lollipopInterface)

    def OnLeftDoubleClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):
        from umlshapes.eventengine.UmlEventEngine import UmlEventEngine

        super().OnLeftDoubleClick(x=x, y=y, keys=keys, attachment=attachment)

        umlLollipopInterface: UmlLollipopInterface = self.GetShape()
        umlFrame:             UmlClassDiagramFrame = umlLollipopInterface.GetCanvas()

        umlLollipopInterface.selected = False
        umlFrame.refresh()

        self.logger.info(f'{umlLollipopInterface=}')

        eventEngine:    UmlEventEngine = umlFrame.eventEngine
        pyutInterfaces: PyutInterfaces = self.getLollipopInterfaces()
        with DlgEditInterface(parent=umlFrame, oglInterface2=umlLollipopInterface, eventEngine=eventEngine, pyutInterfaces=pyutInterfaces, editMode=True) as dlg:
            if dlg.ShowModal() == OK:
                umlFrame.refresh()

    def getLollipopInterfaces(self) -> PyutInterfaces:
        """
        TODO:  Unintended Coupling
        Should this be exposed this way?

        Returns:  The interfaces that are on the board

        """
        umlLollipopInterface: UmlLollipopInterface = self.GetShape()
        umlFrame:             UmlClassDiagramFrame = umlLollipopInterface.GetCanvas()

        umlShapes:      UmlShapeList   = umlFrame.umlShapes
        pyutInterfaces: PyutInterfaces = PyutInterfaces([])

        for umlShape in umlShapes:

            if isinstance(umlShape, UmlLollipopInterface):
                lollipopInterface: UmlLollipopInterface = umlShape
                pyutInterface:     PyutInterface = lollipopInterface.pyutInterface

                if pyutInterface.name != '' or len(pyutInterface.name) > 0:
                    if pyutInterface not in pyutInterfaces:
                        pyutInterfaces.append(pyutInterface)

        return pyutInterfaces
