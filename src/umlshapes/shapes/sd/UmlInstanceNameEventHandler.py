
from logging import Logger
from logging import getLogger


from wx import OK

from umlmodel.SDInstance import SDInstance

from umlshapes.lib.ogl import ShapeEvtHandler

from umlshapes.dialogs.DlgEditInstanceName import DlgEditInstanceName

from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.shapes.sd.UmlInstanceName import UmlInstanceName


class UmlInstanceNameEventHandler(ShapeEvtHandler):
    """
    """

    def __init__(self, umlInstanceName: UmlInstanceName, sdInstance: SDInstance, previousEventHandler: ShapeEvtHandler):

        self.logger: Logger = getLogger(__name__)

        super().__init__(prev=previousEventHandler, shape=umlInstanceName)

        self._sdInstance: SDInstance = sdInstance

    def OnLeftDoubleClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):

        super().OnLeftDoubleClick(x=x, y=y, keys=keys, attachment=attachment)

        umlInstanceName: UmlInstanceName = self.GetShape()

        umlFrame:  UmlFrame  = umlInstanceName.GetCanvas()

        with DlgEditInstanceName(umlFrame, sdInstance=self._sdInstance) as dlg:
            if dlg.ShowModal() == OK:
                self._sdInstance = dlg.sdInstance

                umlInstanceName.sdInstance = dlg.sdInstance
                umlFrame.refresh()
