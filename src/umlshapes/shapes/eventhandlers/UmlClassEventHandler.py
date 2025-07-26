
from typing import cast

from logging import Logger
from logging import getLogger

from wx import OK

from pyutmodelv2.PyutClass import PyutClass

from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame
from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.shapes.UmlClassMenuHandler import UmlClassMenuHandler

from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler


class UmlClassEventHandler(UmlBaseEventHandler):
    """
    Nothing special here;  Just some syntactic sugar
    """

    def __init__(self):
        self.baseLogger:   Logger         = getLogger(__name__)
        self._preferences: UmlPreferences = UmlPreferences()
        super().__init__()

        self._menuHandler: UmlClassMenuHandler = cast(UmlClassMenuHandler, None)

    def OnLeftClick(self, x: int, y: int, keys=0, attachment=0):
        """
        This handler is here only to pass any left clicks to the UML Frame if
        we are in `requesting a lollipop interface mode`. The UML Frame handles
        Left clicks outside the UML Class

        Args:
            x:
            y:
            keys:
            attachment:
        """
        umlClass: UmlClass              = self.GetShape()
        umlFrame: ClassDiagramFrame  = umlClass.GetCanvas()
        """

        I really don't like accessing the UML Frame is this manner because
        now we are tightly coupled; The alternative is sending a message
        That seems complicated in that now the UML Frame must have 2 ways to 
        get the lollipop location
        
        TODO:  May revisit this later

        Pass it to the frame Handler
        """
        if umlFrame.requestingLollipopLocation:
            umlFrame.OnLeftClick(x=x, y=y, keys=keys)
        else:
            super().OnLeftClick(x=x, y=y, keys=keys)

    def OnRightClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):

        super().OnRightClick(x=x, y=y, keys=keys, attachment=attachment)

        umlClass: UmlClass = self.GetShape()
        umlFrame: ClassDiagramFrame  = umlClass.GetCanvas()

        if self._menuHandler is None:
            self._menuHandler = UmlClassMenuHandler(umlClass=umlClass, umlPubSubEngine=umlFrame.umlPubSubEngine)

        self._menuHandler.popupMenu(x=x, y=y)

    def OnLeftDoubleClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):

        from umlshapes.dialogs.umlclass.DlgEditClass import DlgEditClass
        from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

        super().OnLeftDoubleClick(x=x, y=y, keys=keys, attachment=attachment)

        umlClass:  UmlClass  = self.GetShape()
        pyutClass: PyutClass = umlClass.pyutClass
        umlFrame:  ClassDiagramFrame  = umlClass.GetCanvas()

        eventEngine: IUmlPubSubEngine = umlFrame.umlPubSubEngine
        with DlgEditClass(parent=umlFrame, pyutClass=pyutClass, eventEngine=eventEngine) as dlg:
            if dlg.ShowModal() == OK:
                umlFrame.refresh()
