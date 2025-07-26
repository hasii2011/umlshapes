
from logging import Logger
from logging import getLogger

from wx import OK

from pyutmodelv2.PyutModelTypes import ClassName
from pyutmodelv2.PyutInterface import PyutInterface
from pyutmodelv2.PyutInterface import PyutInterfaces

from umlshapes.dialogs.DlgEditInterface import DlgEditInterface

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame

from umlshapes.links.UmlInterface import UmlInterface
from umlshapes.links.UmlLollipopInterface import UmlLollipopInterface

from umlshapes.shapes.UmlClass import UmlClass

from umlshapes.types.Common import UmlShapeList

from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler


class UmlLollipopInterfaceEventHandler(UmlBaseEventHandler):

    def __init__(self, lollipopInterface: UmlLollipopInterface):

        self.logger: Logger = getLogger(__name__)
        super().__init__(shape=lollipopInterface)

    def OnLeftDoubleClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):

        super().OnLeftDoubleClick(x=x, y=y, keys=keys, attachment=attachment)

        umlLollipopInterface: UmlLollipopInterface = self.GetShape()
        umlFrame:             ClassDiagramFrame = umlLollipopInterface.GetCanvas()

        umlLollipopInterface.selected = False
        umlFrame.refresh()

        self.logger.info(f'{umlLollipopInterface=}')

        eventEngine:    IUmlPubSubEngine = umlFrame.umlPubSubEngine
        pyutInterfaces: PyutInterfaces = self.getDefinedInterfaces()
        with DlgEditInterface(parent=umlFrame, oglInterface2=umlLollipopInterface, eventEngine=eventEngine, pyutInterfaces=pyutInterfaces, editMode=True) as dlg:
            if dlg.ShowModal() == OK:
                umlFrame.refresh()

    def getDefinedInterfaces(self) -> PyutInterfaces:
        """
        This will not only look for lollipop interfaces but will find UmlInterfaces.
        It will convert those PyutLink's to PyutInterfaces

        TODO:  Unintended Coupling
        Should this be exposed this way?

        Returns:  The interfaces that are on the board

        """
        umlLollipopInterface: UmlLollipopInterface = self.GetShape()
        umlFrame:             ClassDiagramFrame = umlLollipopInterface.GetCanvas()

        umlShapes:      UmlShapeList   = umlFrame.umlShapes
        pyutInterfaces: PyutInterfaces = PyutInterfaces([])

        for umlShape in umlShapes:

            if isinstance(umlShape, UmlLollipopInterface):
                lollipopInterface: UmlLollipopInterface = umlShape
                pyutInterface:     PyutInterface = lollipopInterface.pyutInterface

                if pyutInterface.name != '' or len(pyutInterface.name) > 0:
                    if pyutInterface not in pyutInterfaces:
                        pyutInterfaces.append(pyutInterface)
            elif isinstance(umlShape, UmlInterface):
                umlInterface: UmlInterface = umlShape
                interface:    UmlClass     = umlInterface.interfaceClass
                implementor:  UmlClass     = umlInterface.implementingClass
                #
                # Convert to PyutInterface
                #
                pyutInterface = PyutInterface(name=interface.pyutClass.name)
                pyutInterface.addImplementor(ClassName(implementor.pyutClass.name))

                pyutInterfaces.append(pyutInterface)

        return pyutInterfaces
