
from logging import Logger
from logging import getLogger

from wx import OK

from pyutmodelv2.PyutNote import PyutNote

from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler
from umlshapes.dialogs.DlgEditNote import DlgEditNote
from umlshapes.frames.UmlFrame import UmlFrame
from umlshapes.shapes.UmlNote import UmlNote


class UmlNoteEventHandler(UmlBaseEventHandler):
    """
    Nothing special here;  Just some syntactic sugar
    """
    def __init__(self):
        self.logger: Logger = getLogger(__name__)
        super().__init__()

    def OnLeftDoubleClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):

        super().OnLeftDoubleClick(x=x, y=y, keys=keys, attachment=attachment)

        umlNote:  UmlNote  = self.GetShape()
        pyutNote: PyutNote = umlNote.pyutNote

        umlFrame:  UmlFrame  = umlNote.GetCanvas()

        with DlgEditNote(parent=umlFrame, pyutNote=pyutNote,) as dlg:
            if dlg.ShowModal() == OK:
                umlFrame.refresh()

        umlNote.selected = False
