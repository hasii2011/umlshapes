
from typing import cast

from logging import Logger
from logging import getLogger

from pyutmodelv2.PyutClass import PyutClass
from wx import OK

from umlshapes.frames.UmlClassDiagramFrame import UmlClassDiagramFrame
from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.shapes.UmlClassMenuHandler import UmlClassMenuHandler

from umlshapes.eventhandlers.UmlBaseEventHandler import UmlBaseEventHandler


class UmlClassEventHandler(UmlBaseEventHandler):
    """
    Nothing special here;  Just some syntactic sugar
    """

    def __init__(self):
        self.logger:       Logger         = getLogger(__name__)
        self._preferences: UmlPreferences = UmlPreferences()
        super().__init__()

        self._menuHandler: UmlClassMenuHandler = cast(UmlClassMenuHandler, None)

    def OnRightClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):

        super().OnRightClick(x=x, y=y, keys=keys, attachment=attachment)

        umlClass: UmlClass = self.GetShape()
        umlFrame:  UmlClassDiagramFrame  = umlClass.GetCanvas()

        if self._menuHandler is None:
            self._menuHandler = UmlClassMenuHandler(umlClass=umlClass, eventEngine=umlFrame.eventEngine)

        self._menuHandler.popupMenu(x=x, y=y)

    def OnLeftDoubleClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):

        from umlshapes.dialogs.DlgEditClass import DlgEditClass

        super().OnLeftDoubleClick(x=x, y=y, keys=keys, attachment=attachment)

        umlClass:  UmlClass  = self.GetShape()
        pyutClass: PyutClass = umlClass.pyutClass
        umlFrame:  UmlClassDiagramFrame  = umlClass.GetCanvas()

        with DlgEditClass(umlFrame, pyutClass) as dlg:
            if dlg.ShowModal() == OK:
                umlFrame.refresh()
