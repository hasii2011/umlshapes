
from typing import Optional

from logging import Logger
from logging import getLogger

from wx import ID_OK

from wx.lib.ogl import ShapeEvtHandler

from umlmodel.Class import Class

from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame
from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.shapes.UmlClassMenuHandler import UmlClassMenuHandler

from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler


class UmlClassEventHandler(UmlBaseEventHandler):
    """
    Nothing special here;  Just some syntactic sugar
    """

    def __init__(self, previousEventHandler: ShapeEvtHandler):

        self.baseLogger:   Logger         = getLogger(__name__)
        self._preferences: UmlPreferences = UmlPreferences()

        super().__init__(previousEventHandler=previousEventHandler)

        self._menuHandler: Optional[UmlClassMenuHandler] = None

    def OnRightClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):

        super().OnRightClick(x=x, y=y, keys=keys, attachment=attachment)

        umlClass: UmlClass          = self.GetShape()
        umlFrame: ClassDiagramFrame = umlClass.GetCanvas()

        if self._menuHandler is None:
            self._menuHandler = UmlClassMenuHandler(umlClass=umlClass, umlPubSubEngine=umlFrame.umlPubSubEngine)

        assert self._menuHandler is not None, 'Yes, we really did initialize it'
        self._menuHandler.popupMenu(x=x, y=y)

    def OnLeftDoubleClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):

        from umlshapes.dialogs.umlclass.DlgEditClass import DlgEditClass
        from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

        super().OnLeftDoubleClick(x=x, y=y, keys=keys, attachment=attachment)

        umlClass:   UmlClass          = self.GetShape()
        modelClass: Class             = umlClass.modelClass
        umlFrame:   ClassDiagramFrame = umlClass.GetCanvas()

        eventEngine: IUmlPubSubEngine = umlFrame.umlPubSubEngine
        with DlgEditClass(parent=umlFrame, modelClass=modelClass, umlPubSubEngine=eventEngine) as dlg:
            if dlg.ShowModal() == ID_OK:
                umlFrame.refresh()
